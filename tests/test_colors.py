import pynesthesia.colors as colors


def test_characters_get_different_colors():
    """Make sure that different colors assigned to each hex character"""
    assert len(set(colors.COLORS.values())) == 16


def test_uppercase_matches_lowercase():
    """Make sure that uppercase (A) and lowercase(a) get the same color"""
    assert colors.colorize("A") == "\033[38;5;27mA\033[0m"


def test_other_characters_are_gray():
    """Make sure that non-hex (z) character is gray"""
    assert colors.colorize("z") == "\033[38;5;245mz\033[0m"


def test_colorize_short_output():
    """Test colorize for small input"""
    assert colors.colorize("0f") == "\033[38;5;196m0\033[38;5;201mf\033[0m"


