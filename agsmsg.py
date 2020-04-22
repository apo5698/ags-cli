class style:
    """
    All styles are in ANSI escape code.
    """
    class color():
        black = 30
        red = 31
        green = 32
        yellow = 33
        blue = 34
        purple = 35
        cyan = 36
        white = 37

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
        return f'\x1b[{color}m{msg}\x1b[0m'


def info(msg, end='\n', color=style.color.green):
    """ Print a information message (Default color green). """
    print(f'{style.stylize(color, f"INFO")}  {msg}', end=end, flush=True)


def fail(msg, end='\n', color=style.color.red):
    """ Print a failing message (Default color red). """
    print(f'{style.stylize(color, f"FAIL")}  {msg}', end=end, flush=True)


def fatal(msg):
    """ Print a failing message (Default color red) then exit with code 1. """
    fail(msg)
    exit(1)


def warn(msg, end='\n', color=style.color.yellow):
    """ Print a warning message (Default color yellow). """
    print(f'{style.stylize(color, f"WARN")}  {msg}', end=end, flush=True)


def name(name_, swap=False, end='\n'):
    """ Return the name in brackets. For example:\n
    ```text
    [abc def]
    [abc-def ghi]
    ```
    """
    name_ = name_.split('/')[1] if 'submission/' in name_ else name_
    name_ = ' '.join(reversed(name_.split(' '))) if swap else name_
    return f'[{name_}]'


def press_continue(button='return'):
    """ Press a button to continue. """
    info(f'Press <{button}> to continue')
    input()


def warn_index(index, msg, color=style.color.yellow):
    """ Print "[`index`] message" (Yellow). """
    print(style.stylize(color, f'[{index}] {msg}'), flush=True)


# Methods below only return string #

def bold(msg):
    """ Return the bold message. """
    return style.stylize(style.font.bold, msg)


def underline(msg):
    """ Return the message with underline. """
    return style.stylize(style.font.underline, msg)


def ask_yn(msg, type_='info'):
    """ Prompts the user for yes (Y/y) or no (N/n).
    Returns `True` if entering Y or y, `False` otherwise.
    """
    text = f'{msg} [Y/n]: '
    if type_ == 'info':
        info(text, '')
    elif type_ == 'warn':
        warn(text, '')
    elif type_ == 'fail':
        fail(text, '')

    option = input().lower()
    while option != 'y' and option != 'n':
        fail(f'Invalid option: {option}. Please try again: ', '')
        option = input().lower()
    return option == 'y'


def ask_retry():
    """ Ask for retry. """
    return ask_yn('Retry?')


def ask_index(start, end):
    """ Prompt the user for numbers. 
    Return it if is a valid index, `None` otherwise.
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


def index_list(list, skip=True):
    """ Print an indexed list. For example:\n
    ```text
    [0] abc
    [1] def
    [2] ghi
    [3] Skip
    ```
    If `skip` set to `False`, `[x] Skip` option will not be displayed.
    """
    for i, l in enumerate(list):
        print(f'[{i}] {underline(l)}')
    if skip:
        print(f'[{i + 1}] Skip')


def textbar(msg, length=3):
    """ Print a message with spaces and vertical bar before it. For example:\n
    ```text
      5 | This is a message
    123 | This is another message
    ```
    """
    print(f'{" " * length} | {msg}', end='\r')


def align_left(msg, length):
    """ Align the message to left. """
    return f'{msg:<{length}}'


def align_center(msg, length):
    """ Align the message to center. """
    return f'{msg:^{length}}'


def align_right(msg, length):
    """ Align the message to right. """
    return f'{msg:>{length}}'
