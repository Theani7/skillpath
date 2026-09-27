"""Unified AI provider layer.

Supports Google Gemini and any OpenAI-compatible endpoint (OpenAI, Groq,
Together, OpenRouter, local Ollama, etc). Callers ask for JSON and the
provider chain tries each configured provider in order until one succeeds.

Selection:
    AI_PROVIDERS=gemini,openai   # ordered fallback chain (default)
    OPENAI_API_KEY=...           # required for the openai provider
    OPENAI_BASE_URL=https://api.openai.com/v1   # override for compatible endpoints
    OPENAI_MODEL=gpt-4o-mini     # default model for the openai provider
"""

import os
import json
import logging

logger = logging.getLogger("resume-analyzer")

# ---------------------------------------------------------------------------
# Gemini provider
# ---------------------------------------------------------------------------
class GeminiProvider:
    name = "gemini"

    def __init__(self):
        self.model = None
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if api_key and api_key != "test-key":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
            self.model = genai.GenerativeModel(model_name)
            self._genai = genai
            logger.info(f"Gemini provider configured with model {model_name}.")
        else:
            logger.warning("Gemini provider disabled (GEMINI_API_KEY not set).")

    def available(self) -> bool:
        return self.model is not None

    def generate_json(self, prompt: str, schema: dict = None, temperature: float = 0.2) -> dict:
        if not self.available():
            return {}
        cfg_kwargs = {"temperature": temperature, "response_mime_type": "application/json"}
        if schema is not None:
            cfg_kwargs["response_schema"] = schema
        response = self.model.generate_content(
            prompt,
            generation_config=self._genai.types.GenerationConfig(**cfg_kwargs),
        )
        if not response or not response.text:
            logger.error("Gemini returned empty response")
            return {}
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}")
            return {}
        return data if isinstance(data, dict) else {}

    def chat(self, messages: list, temperature: float = 0.7, json_mode: bool = False) -> str:
        if not self.available():
            return ""
        sys_text = next((m["content"] for m in messages if m.get("role") == "system"), "")
        user_text = "\n\n".join(m["content"] for m in messages if m.get("role") == "user")
        prompt = f"{sys_text}\n\n{user_text}" if sys_text else user_text
        cfg_kwargs = {"temperature": temperature}
        if json_mode:
            cfg_kwargs["response_mime_type"] = "application/json"
        response = self.model.generate_content(
            prompt,
            generation_config=self._genai.types.GenerationConfig(**cfg_kwargs),
        )
        return response.text if response and response.text else ""


# ---------------------------------------------------------------------------
# OpenAI-compatible provider (OpenAI, Groq, Together, Ollama, ...)
# ---------------------------------------------------------------------------
class OpenAICompatibleProvider:
    name = "openai"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        if self.api_key:
            import httpx
            self._httpx = httpx
            self.client = httpx.Client(timeout=60.0)
            logger.info(f"OpenAI-compatible provider configured ({self.base_url}, {self.model}).")
        else:
            self.client = None
            logger.warning("OpenAI-compatible provider disabled (OPENAI_API_KEY not set).")

    def available(self) -> bool:
        return self.client is not None

    def generate_json(self, prompt: str, schema: dict = None, temperature: float = 0.2) -> dict:
        if not self.available():
            return {}
        # OpenAI-compatible endpoints don't natively enforce a JSON schema the
        # way Gemini does; we ask for JSON in the prompt and rely on JSON mode.
        system = (
            "You are a precise assistant. Respond with ONLY valid JSON, "
            "no markdown or code fences."
        )
        if schema is not None:
            system += f" Conform strictly to this JSON schema: {json.dumps(schema)}"
        try:
            resp = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={
                    "model": self.model,
                    "temperature": temperature,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI-compatible request failed: {e}")
            return {}
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI-compatible JSON response: {e}")
            return {}
        return data if isinstance(data, dict) else {}

    def chat(self, messages: list, temperature: float = 0.7, json_mode: bool = False) -> str:
        if not self.available():
            return ""
        payload = {
            "model": self.model,
            "temperature": temperature,
            "messages": messages,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        try:
            resp = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"] or ""
        except Exception as e:
            logger.error(f"OpenAI-compatible chat failed: {e}")
            return ""


_PROVIDERS = None


def _build_providers():
    global _PROVIDERS
    if _PROVIDERS is not None:
        return _PROVIDERS
    order = [p.strip().lower() for p in os.getenv("AI_PROVIDERS", "gemini,openai").split(",") if p.strip()]
    registry = {"gemini": GeminiProvider, "openai": OpenAICompatibleProvider}
    built = []
    for key in order:
        cls = registry.get(key)
        if cls is None:
            logger.warning(f"Unknown AI provider '{key}' in AI_PROVIDERS; skipping.")
            continue
        try:
            built.append(cls())
        except Exception as e:
            logger.error(f"Failed to initialize provider '{key}': {e}")
    _PROVIDERS = built
    return _PROVIDERS


def generate_json(prompt: str, schema: dict = None, temperature: float = 0.2,
                  _providers=None) -> dict:
    """Try each configured provider in order; return first successful JSON dict."""
    providers = _providers if _providers is not None else _build_providers()
    last_err = None
    for provider in providers:
        if not provider.available():
            continue
        try:
            result = provider.generate_json(prompt, schema=schema, temperature=temperature)
            if result:
                return result
        except Exception as e:
            last_err = e
            logger.warning(f"Provider '{provider.name}' failed: {e}")
    if last_err:
        logger.error(f"All AI providers failed. Last error: {last_err}")
    return {}


def chat(messages: list, temperature: float = 0.7, json_mode: bool = False,
          _providers=None) -> str:
    """Try each configured provider in order; return first successful text."""
    providers = _providers if _providers is not None else _build_providers()
    for provider in providers:
        if not provider.available():
            continue
        try:
            result = provider.chat(messages, temperature=temperature, json_mode=json_mode)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Provider '{provider.name}' chat failed: {e}")
    logger.error("All AI providers failed for chat request.")
    return ""


def active_providers() -> list:
    return [p.name for p in _build_providers() if p.available()]
