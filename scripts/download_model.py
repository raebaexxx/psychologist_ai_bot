import logging
import os
import sys

logging.disable(logging.CRITICAL)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

SAVED = {}


def _clear_proxies():
    for key in ("all_proxy", "ALL_PROXY", "http_proxy", "HTTP_PROXY"):
        v = os.environ.pop(key, None)
        if v is not None:
            SAVED[key] = v


def _restore_proxies():
    os.environ.update(SAVED)


def main():
    model_size = sys.argv[1] if len(sys.argv) > 1 else "medium"
    repo_id = f"Systran/faster-whisper-{model_size}"

    print(f"Downloading {repo_id}...")
    print("Caching at ~/.cache/huggingface/hub/")
    print("Model size: ~1.5 GB\n")

    _clear_proxies()
    try:
        from huggingface_hub import snapshot_download, login

        snapshot_download(repo_id)
        print(f"\nModel {repo_id} downloaded successfully!")
    except ValueError as e:
        print(f"\nProxy error: {e}")
        print("Trying without proxies...")
        for key in ("all_proxy", "ALL_PROXY", "http_proxy", "HTTP_PROXY",
                     "https_proxy", "HTTPS_PROXY"):
            os.environ.pop(key, None)
        try:
            from huggingface_hub import snapshot_download
            snapshot_download(repo_id)
            print(f"\nModel {repo_id} downloaded successfully!")
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
