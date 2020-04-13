class style:
    class color():
        black = 90
        red = 91
        green = 92
        yellow = 93
        blue = 94
        purple = 95
        cyan = 96
        white = 97

    class font():
        bold = 1
        italic = 2
        underline = 4
        strike = 9

    @staticmethod
    def stylize(color, msg):
        """ Return msg with specified color.
        Must use pre-defined color/format constants.
        """

        return f'\33[{color}m{msg}\33[0m'


def info(msg, end='\n', color=style.color.green):
    """ Print "[INFO] message" (Green). """

    print(f'{style.stylize(color, f"[INFO]")} {msg}', end=end, flush=True)


def fail(msg, end='\n', color=style.color.red):
    """ Print "[FAIL] message" (Red). """

    print(f'{style.stylize(color, f"[FAIL]")} {msg}', end=end, flush=True)


def fatal(msg):
    """ Print "[FAIL] message" (Red) and exits with code 1. """

    fail(msg)
    exit(1)


def warn(msg, end='\n', color=style.color.yellow):
    """ Print "[WARN] message" (Yellow). """

    print(f'{style.stylize(color, f"[WARN]")} {msg}', end=end, flush=True)


def name(msg, color=style.color.purple):
    """ Print "[NAME] message" (Purple). """

    print(f'{style.stylize(color, f"[NAME]")} {msg}', flush=True)


def press_continue(button='return'):
    info(f'Press <{button}> to continue')
    input()


def warn_index(index, msg, color=style.color.yellow):
    """ Print "[`index`] message" (Yellow). """

    print(style.stylize(color, f'[{index}] {msg}'), flush=True)


# Methods below only return string #

def bold(msg):
    """ Return the bold message. """

    return style.stylize(style.BOLD, msg)


def underline(msg):
    """ Return the message with underline. """

    return style.stylize(style.font.underline, msg)


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
    return ask_yn('Retry?')


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
