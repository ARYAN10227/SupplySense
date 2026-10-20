"""
Shared pytest setup.

Points the app at a throwaway SQLite database and disables every external
AI provider, so the suite runs offline and never touches real data.
"""

import os
import sys
import tempfile

_tmpdir = tempfile.mkdtemp(prefix="supplysense-tests-")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmpdir}/test.db"
os.environ["DEBUG"] = "false"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
for key in ("GEMINI_API_KEY", "OPENROUTER_API_KEY", "SERPER_API_KEY"):
    os.environ[key] = ""

# Make `import main`, `import services...` work when running from repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
