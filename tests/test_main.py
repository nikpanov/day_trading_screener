import subprocess
import sys
import os

def test_main_runs_as_script(monkeypatch):
    main_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
    result = subprocess.run([sys.executable, main_path, "--dry-run"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Running screener" in result.stdout or "DEBUG" in result.stdout
