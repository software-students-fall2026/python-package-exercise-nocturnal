# set colors for each character
COLORS = {
    "0": 196, "1": 202, "2": 208, "3": 214,
    "4": 226, "5": 154, "6": 46, "7": 49,
    "8": 51, "9": 39, "a": 27, "b": 57,
    "c": 93, "d": 129, "e": 165, "f": 201,
}

def colorize(text: str) -> str:
    """add a color for each character of the text in terminal"""
    colored = ""
    for char in text:
        # hex characters get their own color, otherwise gray
        color = COLORS.get(char.lower(), 245)
        # switch the terminal to this character's color
        start_color = "\033[38;5;" + str(color) + "m"
        colored += start_color + char
    # switch terminal back to the normal color
    return colored + "\033[0m"
