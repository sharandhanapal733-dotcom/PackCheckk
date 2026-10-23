import os
from pathlib import Path

# Root backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)

# Load .env file manually if exists
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

class Settings:
    BASE_DIR: Path = BASE_DIR
    DATABASE_URL: str = get_env("DATABASE_URL", "postgresql://postgres:Nisha2536@localhost:5432/packcheck")
    SECRET_KEY: str = get_env("SECRET_KEY", "packcheck_super_secret_jwt_key_legal_metrology_2026_sih")
    ALGORITHM: str = get_env("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    
    UPLOAD_DIR: Path = BASE_DIR / get_env("UPLOAD_DIR", "uploads")
    REPORT_DIR: Path = BASE_DIR / get_env("REPORT_DIR", "reports")
    
    OCR_ENGINE: str = get_env("OCR_ENGINE", "paddleocr")
    OCR_FALLBACK_ENGINE: str = get_env("OCR_FALLBACK_ENGINE", "tesseract")
    OCR_MIN_CONFIDENCE: float = float(get_env("OCR_MIN_CONFIDENCE", "0.55"))

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORT_DIR.mkdir(parents=True, exist_ok=True)
