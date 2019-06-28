import os


def make_dir(abs_path: str):
    """
    Create a directory with deep path.

    Parameters
    ----------
    abs_path: absolute path of directory.

    """
    dir_path = "/"
    for path in abs_path.split("/"):
        dir_path = os.path.join(dir_path, path)
        if os.path.isdir(dir_path):
            continue
        else:
            os.mkdir(dir_path)
