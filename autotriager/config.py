import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'Bank'
MODEL='gemini-3.1-flash-lite'
EVIRCA_REV='bc11c06932717751f68b8ed7da6d31f5c23c952c'
MAX_STEPS=6
TIMEOUT=60

def api_key():
    value=os.environ.get('GEMINI_API_KEY','').strip()
    if not value and os.name=='nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Environment') as key:
                value=winreg.QueryValueEx(key,'GEMINI_API_KEY')[0].strip()
        except OSError:
            pass
    return value
