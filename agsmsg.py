class Color:
    # Font style
    BOLD = 1
    ITALIC = 2
    UNDERLINE = 4
    STRIKETHROUGH = 9

    # Colors
    BLACK = 90
    RED = 91
    GREEN = 92
    YELLOW = 93
    BLUE = 94
    PURPLE = 95
    CYAN = 96
    WHITE = 97


    @staticmethod
    def colorize(color, msg):
        """ Return msg with specified color. 
        Must use pre-defined color/format constants. 
        """

        return f"\33[{color}m{msg}\33[0m"


def info(msg, ending="\n"):
    """ Print "[INFO] message" (Green). """

    print(f"{Color.colorize(Color.GREEN, f'[INFO] ')}{msg}", end=ending)


def fail(msg, ending="\n"):
    """ Print "[FAIL] message" (Red). """

    print(f"{Color.colorize(Color.RED, f'[FAIL] ')}{msg}", end=ending)


def fatal(msg):
    """ Print "[FAIL] message" (Red) and exits with code 1. """

    fail(msg)
    exit(1)


def warn(msg, ending="\n"):
    """ Print "[WARN] message" (Yellow). """

    print(f"{Color.colorize(Color.YELLOW, f'[WARN] ')}{msg}", end=ending)


def name(msg):
    """ Print "[NAME] message" (Purple). """

    print(f"{Color.colorize(Color.PURPLE, f'[NAME] ')}{msg}")


def warn_index(index, msg):
    """ Print "[`index`] message" (Yellow). """

    print(Color.colorize(Color.YELLOW, f"[{index}] {msg}"))


### Methods below only return processed string ###

def bold(msg):
    """ Return the bold message. """

    return Color.colorize(Color.BOLD, msg)


def underline(msg):
    """ Return the message with underline. """

    return Color.colorize(Color.UNDERLINE, msg)


def prompt_yn(msg):
    """ Prompts the user for yes (Y/y) or no (N/n).
    Returns `True` if entering yes, `False` otherwise.
    """

    info(f"{msg} [Y/n]: ", "")
    option = input().lower()
    while option != "y" and option != "n":
        fail(f"Invalid option: {option}. Please try again: ", "")
        option = input().lower()
    return True if option == "y" else False


def prompt_index(start, end):
    """ Prompts the user for numbers. 
    Returns it if is a valid input, `None` otherwise.
    """

    option = None
    while True:
        try:
            option = int(input())
        except ValueError:
            fail(f"Invalid option (input must be an integer): {option}")
            continue
        if start <= option <= end:
            break
        fail(f"Invalid option (index out of range): {option}")
    return option
