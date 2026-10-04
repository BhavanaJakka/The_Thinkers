import os
import re
import requests
import tempfile
import zipfile
from backend.scanner.extractor import safe_extract_zip

def parse_github_url(url: str):
    """Extracts owner and repo name from GitHub URL."""
    pattern = r'github\.com/([^/]+)/([^/\s.]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def fetch_github_manifests(repo_url: str, dest_dir: str):
    """
    Downloads zip archive of public GitHub repository safely without executing any code.
    Only manifest/lock files are extracted to dest_dir.
    """
    owner, repo = parse_github_url(repo_url)
    if not owner or not repo:
        raise ValueError("Invalid GitHub repository URL. Format must be https://github.com/owner/repository")

    zip_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        headers['Authorization'] = f"token {github_token}"

    resp = requests.get(zip_url, headers=headers, timeout=30, stream=True)
    if resp.status_code != 200:
        raise ValueError(f"Failed to fetch repository from GitHub (HTTP {resp.status_code}). Ensure the repository is public.")

    # Save to temp zip file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
        for chunk in resp.iter_content(chunk_size=8192):
            tmp_zip.write(chunk)
        tmp_zip_path = tmp_zip.name

    try:
        safe_extract_zip(tmp_zip_path, dest_dir)
    finally:
        if os.path.exists(tmp_zip_path):
            os.remove(tmp_zip_path)
