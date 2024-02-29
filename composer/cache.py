from .backend.filesystem.primitives import (
    make_file,
    append_files,
    read_file,
    write_file,
)


def read_cache(cache_file):
    """Read the cache file."""
    notes = read_file(cache_file, strip_newlines=True).read()
    return notes


def archive_cache(cache_path, archive_cache_path):
    """Append the contents of the cache to the archive cache, and clear the cache."""
    cache_file = read_file(cache_path)
    archive_cache_file = read_file(archive_cache_path)
    separator = "\n" + "\n-----\n" + "\n"
    new_archive = append_files(
        cache_file, archive_cache_file, separator, strip_newlines=True
    )
    write_file(make_file(), cache_path)
    write_file(new_archive, archive_cache_path)
