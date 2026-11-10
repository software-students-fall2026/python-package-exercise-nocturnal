import pytest
import pynesthesia.htmlgen as htmlgen

def test_cards_are_repeatable():
    # The same hash produces the same output
    seed = "1234" * 16
    assert htmlgen.generate_cards(seed) == htmlgen.generate_cards(seed)

def test_different_hashes_produce_different_outputs():
    # Different hashes produce different output
    seed1 = "1234" * 16
    seed2 = "abcd" * 16
    assert htmlgen.generate_cards(seed1) != htmlgen.generate_cards(seed2)

def test_cards_require_a_sha256_hash():
    # Non hex seeds are rejected
    with pytest.raises(ValueError):
        htmlgen.generate_cards("00")
    with pytest.raises(ValueError):
        htmlgen.generate_cards("not hex")


def test_card_elements():
    # Generate cards from hash and check elements
    cards = htmlgen.generate_cards("1234abcd" * 8)

    assert len(cards) == 3
    assert [card["header"] for card in cards] == [
        "Yesterday's Fortune",
        "Today's Fortune",
        "Tomorrow's Fortune"
    ]

    for card in cards:
        assert card["body"]
        assert card["page_color"] in htmlgen.BKG_COLORS
        assert card["card_color"] in htmlgen.BKG_COLORS
        assert card["heading_color"] in htmlgen.FONT_COLORS
        assert card["body_color"] in htmlgen.FONT_COLORS
        assert card["font"] in htmlgen.FONTS
        assert card["corner_decoration"] in htmlgen.CORNER_DECORATIONS
        assert card["border_color"] in htmlgen.FONT_COLORS

def test_html_elements(tmp_path):
    # Write cards to HTML and check elements
    cards = htmlgen.generate_cards("1234abcd" * 8)
    output = tmp_path / "fortunes.html"

    htmlgen.write_html(cards, output)
    page = output.read_text(encoding="utf-8")

    assert 'id="card"' in page
    assert 'id="header"' in page
    assert 'id="fortune"' in page
    assert 'id="deco"' in page
    assert 'id="back"' in page
    assert 'id="next"' in page

    for card in cards:
        assert card["header"] in page
        assert card["body"] in page