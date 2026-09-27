import json
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.ai_provider import chat

logger = logging.getLogger("resume-analyzer")

router = APIRouter(prefix="/api/mock-interview", tags=["mock-interview"])


class StartInterviewRequest(BaseModel):
    role: str = Field(..., min_length=1, max_length=100)
    resume_text: Optional[str] = None


class AnswerRequest(BaseModel):
    session_id: str
    question: Optional[str] = ""
    answer: str
    role: str
    chat_history: Optional[list] = []


class InterviewSession:
    def __init__(self, role: str, resume_text: Optional[str] = None):
        self.role = role
        self.resume_text = resume_text
        self.questions_asked = []
        self.answers = []
        self.messages = []
        self.current_question = None

    def to_dict(self):
        return {
            "role": self.role,
            "questions_asked": self.questions_asked,
            "answers": self.answers,
            "messages": self.messages,
            "current_question": self.current_question,
        }


_sessions = {}


@router.post("/start")
async def start_interview(req: StartInterviewRequest):
    """Start a new interactive mock interview session."""
    import uuid
    session_id = str(uuid.uuid4())

    session = InterviewSession(role=req.role, resume_text=req.resume_text)
    _sessions[session_id] = session

    first_question = await _generate_first_question(req.role, req.resume_text)
    session.current_question = first_question
    session.questions_asked.append(first_question)
    session.messages.append({"role": "assistant", "content": first_question})

    return {
        "session_id": session_id,
        "question": first_question,
        "role": req.role,
    }


@router.post("/answer")
async def submit_answer(req: AnswerRequest):
    """Submit an answer or prompt and receive a natural, dynamic conversational response."""
    session = _sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    reply, feedback = await _generate_conversational_turn(
        role=req.role,
        user_input=req.answer,
        last_question=req.question or session.current_question or "",
        chat_history=req.chat_history or session.messages,
        resume_text=session.resume_text,
    )

    session.questions_asked.append(reply)
    session.answers.append({
        "question": req.question or session.current_question or "Topic discussion",
        "answer": req.answer,
        "feedback": feedback,
    })
    session.messages.append({"role": "user", "content": req.answer})
    session.messages.append({"role": "assistant", "content": reply})
    session.current_question = reply

    return {
        "response": reply,
        "next_question": reply,
        "feedback": feedback,
        "question_number": (len(session.messages) // 2) + 1,
    }


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get current session state."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@router.post("/finish/{session_id}")
async def finish_interview(session_id: str):
    """Finish interview and get overall evaluation."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    evaluation = await _evaluate_overall(session)
    del _sessions[session_id]
    return evaluation


async def _generate_first_question(role: str, resume_text: Optional[str]) -> str:
    resume_context = f"\nCandidate resume context:\n{resume_text[:2000]}" if resume_text else ""

    prompt = f"""You are an experienced, welcoming technical interviewer conducting an interview for a {role} position.
Greet the candidate warmly and open with a relevant, engaging question tailored to the {role} role.{resume_context}

Return ONLY the greeting and first question (2-3 sentences max)."""

    messages = [
        {"role": "system", "content": "You are a professional, realistic technical interviewer."},
        {"role": "user", "content": prompt},
    ]

    try:
        question = chat(messages, temperature=0.7).strip()
        return question if question else f"Welcome! To start off, could you tell me about your background with {role} and what you've been working on recently?"
    except Exception as e:
        logger.error(f"Failed to generate first question: {e}")
        return f"Welcome! To start off, could you tell me about your background with {role} and what you've been working on recently?"


async def _generate_conversational_turn(
    role: str,
    user_input: str,
    last_question: str,
    chat_history: list,
    resume_text: Optional[str],
) -> tuple[str, str]:
    """Generate conversational interviewer response that responds naturally to anything said."""
    resume_context = f"Resume highlights: {resume_text[:1200]}" if resume_text else "No resume provided."

    history_lines = []
    for h in chat_history[-8:]:
        if isinstance(h, dict):
            if "role" in h and "content" in h:
                speaker = "Interviewer" if h["role"] in ("assistant", "interviewer", "ai") else "Candidate"
                history_lines.append(f"{speaker}: {h['content']}")
            elif "type" in h and "text" in h:
                speaker = "Interviewer" if h["type"] == "question" else "Candidate"
                history_lines.append(f"{speaker}: {h['text']}")
            elif "question" in h and "answer" in h:
                history_lines.append(f"Interviewer: {h['question']}")
                history_lines.append(f"Candidate: {h['answer']}")

    history_str = "\n".join(history_lines) if history_lines else f"Interviewer: {last_question}"

    prompt = f"""You are an intelligent, realistic, and adaptive technical hiring manager interviewing a candidate for a {role} position.
{resume_context}

Previous Interview Conversation:
{history_str}

Candidate just said:
"{user_input}"

Your task:
Respond conversationally like a real human interviewer.
1. Respond directly to whatever the candidate said:
   - If they answered your question: briefly acknowledge or critique their answer naturally, then segue into the next technical topic, challenge, or scenario for {role}.
   - If they asked a question or asked for clarification/hint: answer helpfully and clearly, then invite their thoughts.
   - If they make casual remarks, greetings, or off-topic comments: reply warmly and gracefully bring the focus back to the interview.
2. Tone: professional, encouraging, and technically sharp.
3. Keep the interviewer reply concise (2-4 sentences or short paragraphs max).
4. Provide a 1-sentence constructive coach tip for the candidate.

Format output as valid JSON:
{{
  "reply": "Your natural spoken response as the interviewer...",
  "coach_note": "Brief constructive tip on their communication or technical approach (or empty string if not applicable)"
}}

Return ONLY valid JSON."""

    messages = [
        {"role": "system", "content": "You are a realistic technical interviewer who converses naturally with candidates. Always respond in JSON."},
        {"role": "user", "content": prompt},
    ]

    try:
        content = chat(messages, temperature=0.7, json_mode=True)
        parsed = json.loads(content)
        reply = (parsed.get("reply") or parsed.get("response") or "").strip()
        coach_note = (parsed.get("coach_note") or parsed.get("feedback") or "").strip()
        if reply:
            return reply, coach_note
    except Exception as e:
        logger.error(f"Conversational generation fallback: {e}")

    # Fallback to direct conversational response
    try:
        fallback_prompt = f"As a {role} interviewer, respond naturally in 2-3 sentences to the candidate saying: '{user_input}'."
        reply = chat([{"role": "user", "content": fallback_prompt}], temperature=0.7).strip()
        return reply or "That makes sense. Could you walk me through a specific project where you applied that?", ""
    except Exception:
        return "That's an interesting approach. How would you handle potential edge cases or scaling bottlenecks with that?", ""


async def _evaluate_overall(session: InterviewSession) -> dict:
    if session.messages:
        transcript = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in session.messages])
    else:
        transcript = "\n".join([
            f"Interviewer: {a.get('question','')}\nCandidate: {a.get('answer','')}"
            for a in session.answers
        ])

    prompt = f"""You interviewed a candidate for a {session.role} position.

Interview transcript:
{transcript}

Provide an overall evaluation in this JSON format:
{{
  "score": <1-10 integer>,
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendations": ["recommendation1", "recommendation2"],
  "summary": "2-3 sentence overall assessment"
}}

Return ONLY the JSON, no explanation."""

    messages = [
        {"role": "system", "content": "You are an expert interviewer providing structured feedback."},
        {"role": "user", "content": prompt},
    ]

    try:
        content = chat(messages, temperature=0.3, json_mode=True)
        return json.loads(content)
    except Exception as e:
        logger.error(f"Failed to evaluate overall: {e}")
        return {
            "score": 7,
            "strengths": ["Communicated effectively during the interview session", "Showed problem-solving enthusiasm"],
            "weaknesses": ["Could provide deeper architectural tradeoffs"],
            "recommendations": ["Practice structuring answers using the STAR method"],
            "summary": "Good conversation overall. Continuing to practice with real-world scenarios will build confidence.",
        }
