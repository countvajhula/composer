import sys
from time import sleep

PROGRESS_DELAY = 0


def _write_out(message):
    sys.stdout.write(message)
    sys.stdout.flush()


def display_message(
    message=None, newline=True, interactive=False, prompt=False
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
    if newline:
        _write_out('\n')
