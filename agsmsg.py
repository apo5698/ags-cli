class Style:
    class Color:
        BLACK = 90
        RED = 91
        GREEN = 92
        YELLOW = 93
        BLUE = 94
        PURPLE = 95
        CYAN = 96
        WHITE = 97

    # Font style
    BOLD = 1
    ITALIC = 2
    UNDERLINE = 4
    STRIKETHROUGH = 9

    @staticmethod
    def stylize(color, msg):
        """ Return msg with specified color.
        Must use pre-defined color/format constants.
        """

        return f'\33[{color}m{msg}\33[0m'


def info(msg, ending='\n', color=Style.Color.GREEN):
    """ Print "[INFO] message" (Green). """

    print(f"{Style.stylize(color, f'[INFO] ')}{msg}", end=ending)


def fail(msg, ending='\n', color=Style.Color.RED):
    """ Print "[FAIL] message" (Red). """

    print(f'{Style.stylize(color, f"[FAIL]")} {msg}', end=ending)


def fatal(msg):
    """ Print "[FAIL] message" (Red) and exits with code 1. """

    fail(msg)
    exit(1)


def warn(msg, ending='\n', color=Style.Color.YELLOW):
    """ Print "[WARN] message" (Yellow). """

    print(f'{Style.stylize(color, f"[WARN]")} {msg}', end=ending)


def name(msg, color=Style.Color.PURPLE):
    """ Print "[NAME] message" (Purple). """

    print(f'{Style.stylize(color, f"[NAME]")} {msg}')


def press_continue(button='return'):
    info(f'Press <{button}> to continue')
    input()


def warn_index(index, msg, color=Style.Color.YELLOW):
    """ Print "[`index`] message" (Yellow). """

    print(Style.stylize(color, f'[{index}] {msg}'))


# Methods below only return string #

def bold(msg):
    """ Return the bold message. """

    return Style.stylize(Style.BOLD, msg)


def underline(msg):
    """ Return the message with underline. """

    return Style.stylize(Style.UNDERLINE, msg)


def ask_yn(msg, msgtype='info'):
    """ Prompts the user for yes (Y/y) or no (N/n).
    Returns `True` if entering yes, `False` otherwise.
    """

    text = f'{msg} [Y/n]: '
    if msgtype == 'info':
        info(text, '')
    elif msgtype == 'warn':
        warn(text, '')
    elif msgtype == 'fail':
        fail(text, '')

    option = input().lower()
    while option != 'y' and option != 'n':
        fail(f'Invalid option: {option}. Please try again: ', '')
        option = input().lower()
    return True if option == 'y' else False


def ask_retry():
    ask_yn('Retry?')


def ask_index(start, end):
    """ Prompts the user for numbers. 
    Returns it if is a valid input, `None` otherwise.
    """

    option = None
    while True:
        try:
            option = int(input())
        except ValueError:
            fail(f'Invalid option (input must be an integer): {option}')
            continue
        if start <= option <= end:
            break
        fail(f'Invalid option (index out of range): {option}')
    return option
