import sys
from time import sleep

try:  # py2
    raw_input
except NameError:  # py3
    raw_input = input

PROGRESS_DELAY = 0


def _write_out(message):
    sys.stdout.write(message)
    sys.stdout.flush()


def display_message(
    message=None,
    newline=True,
    interactive=False,
    prompt=False,
    acknowledge=False,
):
    """ Show a message to the user.

    :param str message: The message
    :param bool newline: Whether to add a newline after showing the message
    :param bool interactive: Whether to indicate to the user that something is
        in progress in some way (e.g. add ellipses).
    :param bool prompt: Whether to indicate that user input is need in some way
        (e.g. add a suitable preceding symbol to the message)
    """
    if message is None:
        message = ""
    if prompt:
        _write_out(u"\u266A ")
    _write_out(message)
    if interactive:
        for c in "...":
            sleep(PROGRESS_DELAY)
            _write_out(c)
    if acknowledge:
        ask_input()
    if newline:
        _write_out('\n')


def ask_input(message=''):
    """ Ask for input from the user.

    :param str message: The message to prompt the user with
    :returns str: The input from the user
    """
    return raw_input(message)
