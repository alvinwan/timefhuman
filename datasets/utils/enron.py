import os
from pathlib import Path


def iter_enron_paths(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def iter_enron_corpus_chunks(root: Path):
    for path in iter_enron_paths(root):
        relative = path.relative_to(root).as_posix()
        yield f"\n\n--- EMAIL: {relative} ---\n"
        text = path.read_text(encoding="utf-8", errors="ignore")
        yield text
        if not text.endswith("\n"):
            yield "\n"


def build_enron_corpus_text(root: Path):
    return "".join(iter_enron_corpus_chunks(root))


def write_enron_corpus_text(root: Path, destination: Path):
    with destination.open("w", encoding="utf-8") as handle:
        for chunk in iter_enron_corpus_chunks(root):
            handle.write(chunk)


def enron_local_dir_candidates(extracted_dir_name: str, destination_root: Path):
    candidates = []
    enron_root = None
    if "ENRON_ROOT" in os.environ:
        enron_root = Path(os.environ["ENRON_ROOT"]).expanduser()
    if enron_root:
        candidates.append(enron_root)
    candidates.extend([
        Path.home() / "Downloads" / extracted_dir_name,
        destination_root / extracted_dir_name,
    ])
    return candidates


def enron_local_archive_candidates(archive_name: str, destination_root: Path):
    candidates = []
    archive_path = None
    if "ENRON_ARCHIVE" in os.environ:
        archive_path = Path(os.environ["ENRON_ARCHIVE"]).expanduser()
    if archive_path:
        candidates.append(archive_path)
    candidates.extend([
        Path.home() / "Downloads" / archive_name,
        destination_root / archive_name,
    ])
    return candidates
