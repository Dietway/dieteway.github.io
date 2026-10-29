"""Runtime configuration: constants plus settings from .env locally or GitHub Secrets in CI."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
# This repository is private. Publishing runs in a public one (free GitHub Actions and Pages) that holds the queue,
# publisher/, shared/ and the media; PUBLIC_DIR is its local clone (generator/public_repo.py).
PUBLIC_REMOTE = "https://github.com/Dietway/dieteway.github.io.git"
PUBLIC_DIR = ROOT / "public"
TIMEZONE = "America/Sao_Paulo"
VOICE = "pt-BR-ThalitaMultilingualNeural"  # edge-tts, native pt-BR female; never change mid-week
VOICE_RATE = "+8%"  # inside sentences only; the pauses between sentences keep their length
# Voices a reel may pick with its "voice" field (owner, 2026-10-28: vary the voices). Short name -> edge-tts voice.
VOICES = {
    "thalita": "pt-BR-ThalitaMultilingualNeural",
    "remy": "fr-FR-RemyMultilingualNeural",
    "brian": "en-US-BrianMultilingualNeural",
}


@dataclass(frozen=True)
class Settings:
    ig_user_id: str | None
    ig_access_token: str | None
    pages_base_url: str | None
    handle: str


def load_settings(env_file: Path | None = ROOT / ".env") -> Settings:
    if env_file is not None and Path(env_file).exists():
        load_dotenv(env_file, override=False)
    return Settings(
        ig_user_id=os.getenv("IG_USER_ID") or None,
        ig_access_token=os.getenv("IG_ACCESS_TOKEN") or None,
        pages_base_url=(os.getenv("PAGES_BASE_URL") or "").rstrip("/") or None,
        handle=os.getenv("IG_HANDLE", "@diet_way"),
    )


def require(value: str | None, name: str) -> str:
    if not value:
        raise RuntimeError(f"Missing required setting {name}; set it in .env or GitHub Secrets")
    return value
