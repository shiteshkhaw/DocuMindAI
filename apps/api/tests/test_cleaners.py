from cleaners.pipeline import (
    ContentCleanerPipeline,
    DuplicateNewlineNormalizer,
    InvalidCharacterCleaner,
    PageArtifactCleaner,
    UnicodeNormalizer,
    WhitespaceNormalizer,
)


def test_unicode_normalizer() -> None:
    cleaner = UnicodeNormalizer()
    result = cleaner.clean("\u201cDocuMind\u201d \u2014 \u2018intelligent\u2019 \u2013- simple")
    assert result == '"DocuMind" - \'intelligent\' -- simple'


def test_whitespace_normalizer() -> None:
    cleaner = WhitespaceNormalizer()
    result = cleaner.clean("Hello\tworld   with   many    spaces.")
    assert result == "Hello world with many spaces."


def test_duplicate_newline_normalizer() -> None:
    cleaner = DuplicateNewlineNormalizer()
    result = cleaner.clean("Line 1\n\n\n\n\nLine 2")
    assert result == "Line 1\n\nLine 2"


def test_invalid_character_cleaner() -> None:
    cleaner = InvalidCharacterCleaner()
    result = cleaner.clean("Hello\x00\x08World\nWith\tTabs")
    assert result == "HelloWorld\nWith\tTabs"


def test_page_artifact_cleaner() -> None:
    cleaner = PageArtifactCleaner()
    assert "Page 1 of 5" not in cleaner.clean("Some header content\nPage 1 of 5\nBody content")
    assert "- 3 -" not in cleaner.clean("Some content\n- 3 -\nOther content")
    assert "[Page 12]" not in cleaner.clean("[Page 12]\nThis is the content.")
    assert "Page 4" not in cleaner.clean("Page 4\nMore content")


def test_content_cleaner_pipeline() -> None:
    pipeline = ContentCleanerPipeline()
    raw_text = (
        " \t \u201cWelcome to DocuMind AI!\u201d\n\n\n\n"
        "Page 1 of 1\n\n"
        "This is\t\ta  clean  testcase.\x07 "
    )
    cleaned = pipeline.clean(raw_text)
    assert cleaned == '"Welcome to DocuMind AI!"\n\nThis is a clean testcase.'
