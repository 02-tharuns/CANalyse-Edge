from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CANALYSE_", env_file=ROOT / ".env", extra="ignore")
    host: str = "127.0.0.1"
    port: int = 8080
    data_dir: Path = ROOT / "data"
    output_dir: Path = ROOT / "outputs"
    model_path: Path = ROOT / "models" / "condition_model.joblib"


settings = Settings()
