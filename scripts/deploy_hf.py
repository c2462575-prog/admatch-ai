"""Deploy current codebase to HuggingFace Space.

Requires HF_TOKEN environment variable to be set.
Usage: HF_TOKEN=your_token python scripts/deploy_hf.py "commit message"
"""
import shutil, os, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

HF_TOKEN = os.getenv("HF_TOKEN", "")
REPO_ID = os.getenv("HF_SPACE_REPO", "Yc79/admatch-ai")

IGNORE_PATTERNS = [
    "__pycache__", ".git", ".claude", "*.pyc", "nul",
    "data/app.db", "report.md", ".env", ".pytest_cache",
    "Dockerfile.hf", "ITERATION_GUIDE.md", "scripts/deploy_hf.py",
]


def deploy(message="deploy update"):
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN environment variable not set")
        sys.exit(1)

    from huggingface_hub import HfApi

    api = HfApi(token=HF_TOKEN)
    staging = os.path.join(tempfile.gettempdir(), "hf_deploy")
    root = os.path.join(os.path.dirname(__file__), "..")

    if os.path.exists(staging):
        shutil.rmtree(staging)

    ignore = shutil.ignore_patterns(*IGNORE_PATTERNS)
    shutil.copytree(root, staging, ignore=ignore)

    # Swap Dockerfile for HF-specific version
    df = os.path.join(staging, "Dockerfile")
    if os.path.exists(df):
        os.remove(df)
    hf_df = os.path.join(root, "Dockerfile.hf")
    if os.path.exists(hf_df):
        shutil.copy(hf_df, df)

    api.upload_folder(
        folder_path=staging,
        repo_id=REPO_ID,
        repo_type="space",
        commit_message=message,
    )
    shutil.rmtree(staging)
    print(f"Deployed to https://huggingface.co/spaces/{REPO_ID}")


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "deploy update"
    deploy(msg)
