from datasets.utils.enron import build_enron_corpus_text, write_enron_corpus_text


def test_build_enron_corpus_text_sorts_paths_and_normalizes_trailing_newlines(tmp_path):
    root = tmp_path / "enron_mail_20150507"
    (root / "z").mkdir(parents=True)
    (root / "a" / "nested").mkdir(parents=True)

    (root / "z" / "20.").write_text("second file\n", encoding="utf-8")
    (root / "a" / "nested" / "1.").write_text("first file", encoding="utf-8")

    assert build_enron_corpus_text(root) == (
        "\n\n--- EMAIL: a/nested/1. ---\n"
        "first file\n"
        "\n\n--- EMAIL: z/20. ---\n"
        "second file\n"
    )


def test_write_enron_corpus_text_matches_build_helper(tmp_path):
    root = tmp_path / "enron_mail_20150507"
    (root / "maildir").mkdir(parents=True)
    (root / "maildir" / "1.").write_text("body text", encoding="utf-8")
    (root / "maildir" / "2.").write_text("body text 2\n", encoding="utf-8")

    destination = tmp_path / "enron_emails.txt"
    write_enron_corpus_text(root, destination)

    assert destination.read_text(encoding="utf-8") == build_enron_corpus_text(root)
