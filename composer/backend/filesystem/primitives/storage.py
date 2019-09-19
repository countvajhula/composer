import os

PATH_SPECIFICATION = "{path}/{filename}"


def full_file_path(root, filename, dereference=False):
    """ Given a path root and a filename, construct an OS-specific filesystem
    path.

    :param str root: The base path
    :param str filename: The name of the file
    :param bool dereference: If the file is a symbolic link, the constructed
    path could either return the path to the link, or the path to the linked
    original file. If dereference is True, then return the path to the original
    file, otherwise to the link itself without following it.

    :returns str: The constructed path
    """
    if dereference:
        path_fn = os.path.realpath
    else:
        path_fn = os.path.abspath
    return path_fn(PATH_SPECIFICATION.format(path=root, filename=filename))


def read_file(filepath):
    with open(filepath, "r") as f:
        contents = f.read()
    return contents


def write_file(contents, filepath):
    with open(filepath, "w") as f:
        f.write(contents)
