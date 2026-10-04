import os
import zipfile
import shutil
import tempfile
from pathlib import Path

MAX_FILE_COUNT = 5000
MAX_TOTAL_EXTRACTED_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    '.json', '.txt', '.lock', '.xml', '.gradle', '.mod', '.toml', '.yml', '.yaml'
}

def safe_extract_zip(zip_filepath: str, extract_to_dir: str):
    """
    Extracts uploaded zip archive safely:
    - Zip-slip path traversal prevention
    - Symlink rejection
    - File count limit & total uncompressed size limit (zip bomb defense)
    - File extension filter (manifest & config files)
    """
    if not zipfile.is_zipfile(zip_filepath):
        raise ValueError("Invalid file format. Provided file is not a valid zip archive.")

    total_size = 0
    file_count = 0

    with zipfile.ZipFile(zip_filepath, 'r') as zf:
        for member in zf.infolist():
            file_count += 1
            if file_count > MAX_FILE_COUNT:
                raise ValueError(f"Zip bomb protection: Exceeded maximum file count limit of {MAX_FILE_COUNT}.")

            total_size += member.file_size
            if total_size > MAX_TOTAL_EXTRACTED_SIZE:
                raise ValueError("Zip bomb protection: Exceeded maximum uncompressed size limit of 100MB.")

            # Path traversal / Zip slip check
            filename = member.filename
            dest_path = os.path.abspath(os.path.join(extract_to_dir, filename))
            if not dest_path.startswith(os.path.abspath(extract_to_dir)):
                raise ValueError("Security Violation: Zip slip path traversal attempt detected.")

            # Symlink check (external file attributes check)
            is_symlink = (member.external_attr >> 16) & 0o120000 == 0o120000
            if is_symlink:
                continue

            # Only extract manifest / lock / config files or directories
            if not member.is_dir():
                ext = Path(filename).suffix.lower()
                if ext in ALLOWED_EXTENSIONS or filename.lower() in {'pipfile', 'pipfile.lock', 'go.mod', 'cargo.lock', 'yarn.lock'}:
                    zf.extract(member, extract_to_dir)
            else:
                zf.extract(member, extract_to_dir)

def create_temp_extract_dir():
    return tempfile.mkdtemp(prefix="diptrix_scan_")

def cleanup_temp_dir(dirpath: str):
    if dirpath and os.path.exists(dirpath):
        norm_path = os.path.normpath(dirpath).lower()
        # Only cleanup temporary scan folders or uploads temp folders, never fixture dirs
        if 'diptrix_scan_' in norm_path or 'tmp' in norm_path or 'temp' in norm_path or 'uploads' in norm_path:
            try:
                shutil.rmtree(dirpath)
            except Exception as e:
                print(f"[CLEANUP ERROR] Failed to delete temp dir {dirpath}: {e}")
