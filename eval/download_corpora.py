import argparse
import os
import shutil
import tarfile
from pathlib import Path
from urllib.request import urlopen

from eval.corpora import CORPUS_FILES, corpora_dir


ENRON_NAME = "enron_emails"


def _iter_enron_paths(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def _iter_enron_corpus_chunks(root: Path):
    for path in _iter_enron_paths(root):
        relative = path.relative_to(root).as_posix()
        yield f"\n\n--- EMAIL: {relative} ---\n"
        text = path.read_text(encoding="utf-8", errors="ignore")
        yield text
        if not text.endswith("\n"):
            yield "\n"


def build_enron_corpus_text(root: Path):
    return "".join(_iter_enron_corpus_chunks(root))


def write_enron_corpus_text(root: Path, destination: Path):
    with destination.open("w", encoding="utf-8") as handle:
        for chunk in _iter_enron_corpus_chunks(root):
            handle.write(chunk)


def _enron_local_dir_candidates(destination_root: Path):
    info = CORPUS_FILES[ENRON_NAME]
    candidates = []
    enron_root = None
    if "ENRON_ROOT" in os.environ:
        enron_root = Path(os.environ["ENRON_ROOT"]).expanduser()
    if enron_root:
        candidates.append(enron_root)
    candidates.extend([
        Path.home() / "Downloads" / info["extracted_dir_name"],
        destination_root / info["extracted_dir_name"],
    ])
    return candidates


def _enron_local_archive_candidates(destination_root: Path):
    info = CORPUS_FILES[ENRON_NAME]
    candidates = []
    archive_path = None
    if "ENRON_ARCHIVE" in os.environ:
        archive_path = Path(os.environ["ENRON_ARCHIVE"]).expanduser()
    if archive_path:
        candidates.append(archive_path)
    candidates.extend([
        Path.home() / "Downloads" / info["archive_name"],
        destination_root / info["archive_name"],
    ])
    return candidates


def _resolve_existing_enron_root(destination_root: Path):
    for candidate in _enron_local_dir_candidates(destination_root):
        if candidate.exists():
            return candidate
    return None


def _resolve_existing_enron_archive(destination_root: Path):
    for candidate in _enron_local_archive_candidates(destination_root):
        if candidate.exists():
            return candidate
    return None


def _download_to(url: str, destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    print(f"download {url} -> {destination}")
    with urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def _extract_enron_archive(archive_path: Path, destination_root: Path):
    print(f"extract {archive_path} -> {destination_root}")
    with tarfile.open(archive_path, "r:gz") as archive:
        archive.extractall(destination_root)


def download_enron_corpus(destination: Path, force: bool):
    info = CORPUS_FILES[ENRON_NAME]
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        print(f"skip {ENRON_NAME}: {destination}")
        return

    destination_root = destination.parent
    enron_root = _resolve_existing_enron_root(destination_root)
    if enron_root is None:
        archive_path = _resolve_existing_enron_archive(destination_root)
        if archive_path is None:
            archive_path = destination_root / info["archive_name"]
            _download_to(info["download_url"], archive_path)
        _extract_enron_archive(archive_path, destination_root)
        enron_root = _resolve_existing_enron_root(destination_root)
        if enron_root is None:
            raise FileNotFoundError(f"extracted {archive_path} but could not find {info['extracted_dir_name']}")

    print(f"flatten {ENRON_NAME}: {enron_root} -> {destination}")
    write_enron_corpus_text(enron_root, destination)


def download_corpus(name: str, destination: Path, force: bool):
    if name == ENRON_NAME:
        download_enron_corpus(destination, force=force)
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        print(f"skip {name}: {destination}")
        return

    url = CORPUS_FILES[name]["download_url"]
    print(f"download {name}: {url} -> {destination}")
    with urlopen(url) as response:
        destination.write_bytes(response.read())


def main():
    parser = argparse.ArgumentParser(description="Download external evaluation corpora.")
    parser.add_argument("names", nargs="*", choices=sorted(CORPUS_FILES), help="Corpus names to download")
    parser.add_argument("--force", action="store_true", help="Overwrite any cached files")
    args = parser.parse_args()

    names = args.names or sorted(CORPUS_FILES)
    root = corpora_dir()
    for name in names:
        download_corpus(name, root / CORPUS_FILES[name]["cache_name"], force=args.force)


if __name__ == "__main__":
    main()
