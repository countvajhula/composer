import sys
from time import sleep

try:  # py2
    raw_input
except NameError:  # py3
    raw_input = input

PROGRESS_DELAY = 0


def _write_out(message):
    sys.stdout.write(str(message))
    sys.stdout.flush()


def display_message(
    message=None,
    newline=True,
    interactive=False,
    prompt=False,
    acknowledge=False,
    interrupt=False,
):
    """ Show a message to the user.

    :param str message: The message
    :param bool newline: Whether to add a newline after showing the message
    :param bool interactive: Whether to indicate to the user that something is
        in progress in some way (e.g. add ellipses).
    :param bool prompt: Whether to indicate that user input is need in some way
        (e.g. add a suitable preceding symbol to the message)
    :param bool acknowledge: Whether to require acknowledgement from the user
        in the form of keyboard input.
    :param bool interrupt: Whether this message interrupts the flow or is part
        of it. This simply precedes the message with a newline if true.
    """
    if message is None:
        message = ""
    if interrupt:
        _write_out(u"\n")
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
