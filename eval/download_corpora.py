import argparse
from pathlib import Path
from urllib.request import urlopen

from eval.corpora import CORPUS_FILES, corpora_dir


def download_corpus(name: str, destination: Path, force: bool):
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
