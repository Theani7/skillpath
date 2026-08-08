"""Tests for audit security fixes."""
import pytest
from api.database import _ensure_column, ALLOWED_TABLES
from api.routes.analysis import _detect_filetype
from api.security import get_password_hash, verify_password


class TestEnsureColumnWhitelist:
    def test_allowed_table_passes(self):
        """Tables in whitelist should not raise when calling _ensure_column."""
        import psycopg2
        import os
        conn = psycopg2.connect(os.getenv("TEST_DATABASE_URL", "postgresql://localhost:5432/skillpath_test"))
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS test_users")
        cursor.execute("CREATE TABLE test_users (id SERIAL PRIMARY KEY)")
        # Temporarily add to whitelist for test
        from api.database import ALLOWED_TABLES as _orig
        import api.database
        api.database.ALLOWED_TABLES.add("test_users")
        _ensure_column(cursor, "test_users", "new_col", "TEXT")
        cursor.execute("DROP TABLE IF EXISTS test_users")
        api.database.ALLOWED_TABLES.discard("test_users")
        conn.close()

    def test_unknown_table_raises(self):
        """Unknown table should raise ValueError."""
        import psycopg2
        import os
        conn = psycopg2.connect(os.getenv("TEST_DATABASE_URL", "postgresql://localhost:5432/skillpath_test"))
        conn.autocommit = True
        cursor = conn.cursor()
        with pytest.raises(ValueError, match="not in the allowed tables whitelist"):
            _ensure_column(cursor, "malicious_table", "col", "TEXT")
        conn.close()


def _make_ooxml_zip(members):
    """Build an in-memory ZIP containing the given member paths."""
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name in members:
            z.writestr(name, "<x/>")
    return buf.getvalue()


class TestFileTypeDetection:
    def test_pdf_magic_bytes(self):
        assert _detect_filetype(b"%PDF-1.4 fake content", "test.pdf") == "pdf"

    def test_docx_magic_bytes(self):
        """A real OOXML package is accepted."""
        assert _detect_filetype(_make_ooxml_zip(
            ["[Content_Types].xml", "word/document.xml"]), "test.docx") == "docx"

    def test_zip_prefix_alone_is_not_docx(self):
        """PK\\x03\\x04 is the generic ZIP signature, not a DOCX signature.

        xlsx/pptx/jar all start with it. Accepting them here means
        docx.Document() later dies on a missing [Content_Types].xml, which
        surfaces as a 500 instead of a 400.
        """
        assert _detect_filetype(b"PK\x03\x04 fake content", "test.docx") is None
        assert _detect_filetype(_make_ooxml_zip(["xl/workbook.xml"]), "book.xlsx") is None
        assert _detect_filetype(_make_ooxml_zip(["ppt/presentation.xml"]), "deck.pptx") is None

    def test_extension_fallback_removed(self):
        """Extension alone should not determine file type."""
        assert _detect_filetype(b"not a pdf", "test.pdf") is None
        assert _detect_filetype(b"not a docx", "test.docx") is None

    def test_empty_content(self):
        assert _detect_filetype(b"", "test.pdf") is None


class TestPasswordHashing:
    def test_long_password_warning(self, caplog):
        """Passwords over 72 bytes should trigger a warning."""
        import logging
        with caplog.at_level(logging.WARNING):
            get_password_hash("a" * 100)
        assert "exceeds 72 bytes" in caplog.text

    def test_normal_password_no_warning(self, caplog):
        """Normal passwords should not trigger warnings."""
        import logging
        with caplog.at_level(logging.WARNING):
            get_password_hash("normalpassword")
        assert "exceeds 72 bytes" not in caplog.text

    def test_password_verify_works(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
