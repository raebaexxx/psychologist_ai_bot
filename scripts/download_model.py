import logging
import os
import sys
from pathlib import Path

logging.disable(logging.CRITICAL)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

SAVED = {}

HF_TOKEN_HELP = """\n📌 Для ускорения скачивания создай бесплатный токен:
   1. Зайди на https://huggingface.co/settings/tokens
   2. Создай новый token (Read)
   3. Передай его так:
      HF_TOKEN=hf_xxxxx uv run python scripts/download_model.py
   Или добавь в .env:
      HF_TOKEN=hf_xxxxx"""


def _clear_proxies():
    for key in ("all_proxy", "ALL_PROXY", "http_proxy", "HTTP_PROXY"):
        v = os.environ.pop(key, None)
        if v is not None:
            SAVED[key] = v


def _restore_proxies():
    os.environ.update(SAVED)


def _load_env():
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                if val and key not in os.environ:
                    os.environ.setdefault(key, val)


def main():
    model_size = sys.argv[1] if len(sys.argv) > 1 else "medium"
    repo_id = f"Systran/faster-whisper-{model_size}"

    _load_env()
    token = os.environ.get("HF_TOKEN")

    print(f"Downloading {repo_id}...")
    print(f"Caching at ~/.cache/huggingface/hub/")
    print(f"Model size: ~1.5 GB")

    if token:
        print(f"Using HF_TOKEN for authentication (faster downloads)")
    else:
        print(HF_TOKEN_HELP)
    print()

    _clear_proxies()
    try:
        from huggingface_hub import snapshot_download

        kwargs = {"repo_id": repo_id, "resume_download": True}
        if token:
            kwargs["token"] = token

        snapshot_download(**kwargs)
        print(f"\n✅ Model {repo_id} downloaded successfully!")
    except ValueError as e:
        print(f"\nProxy error: {e}")
        for key in ("all_proxy", "ALL_PROXY", "http_proxy", "HTTP_PROXY",
                     "https_proxy", "HTTPS_PROXY"):
            os.environ.pop(key, None)
        try:
            snapshot_download(**kwargs)
            print(f"\n✅ Model {repo_id} downloaded successfully!")
        except Exception as e2:
            print(f"\nError: {e2}")
            sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        _restore_proxies()


if __name__ == "__main__":
    main()
