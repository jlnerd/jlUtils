"""
Utility functions for interacting with files
"""
import os as _os
import yaml as _yaml
import json as _json
import numpy as _np


def list_files(path_dir):
    """
    List the files in a given directory
    
    Args:
        path_dir: string. the path to the directory of interest
        
    Returns:
        path_files: list. list of file paths for the directory of interest
    """

    path_files = []
    for dirname, dirfolders, filenames in _os.walk(path_dir):
        for file in filenames:
            path_files.append(_os.path.join(dirname, file))
    return path_files


def list_dirs(path_dir):
    """
    List the directories in a given directory
    
    Args:
        path_dir: string. the path to the directory of interest
        
    Returns:
        path_dirs: list. list of directories inside the directory of interest
    """

    path_dirs = []
    for dirname, dirfolders, filenames in _os.walk(path_dir):
        path_dirs.append(dirname)
    return path_dirs


def load(fpath):
    """
    Dynamic function for loading arbitrary file formats
    
    Args:
        fpath: The path to a file of interest
        
    Returns:
        output: The file loaded in the appropriate format
    """

    fpath = str(fpath)
    filename = _os.path.basename(fpath)

    if "yaml" in filename or "yml" in filename:

        with open(fpath, "r") as f:
            output = _yaml.load(f, Loader=_yaml.FullLoader)

    elif "json" in filename:

        with open(fpath, "r") as f:
            output = _json.load(f)

    else:
        raise (
            NotImplementedError(
                " ".join(
                    [
                        "The load function could not interpret the necessary method",
                        f"to load the file based on the fpath {fpath}. Consider updating",
                        "the function to handle files of this type",
                    ]
                )
            )
        )

    return output


def save(data, fpath, verbose=1):
    """
    Dynamic function for saving an arbitrary set of data
    as a file type specified by the file extension in the
    `fpath` argument
    
    Args:
        data: dynamic. The data of interest
        fpath: str. The full path for where the file will 
            be saved. If the directory you specify does not
            exist, the function will automatically create it
        verbose: int. print-out verbosity
    
    Returns:
        None. The data will be saved
    """

    # Make the directory if it doesnt exist
    fdir = _os.path.dirname(fpath)
    if not _os.path.isdir(fdir):
        _os.makedirs(fdir)

    # save as yaml
    if ".yaml" in fpath or ".yml" in fpath:

        for key in data:
            if isinstance(data[key], _np.float):
                data[key] = float(data[key])
            for int_type in [_np.int, _np.int8, _np.int16, _np.int32, _np.int64]:
                if isinstance(data[key], _np.int):
                    data[key] = int(data[key])

        with open(fpath, "w") as f:
            _yaml.dump(data, f)

    elif ".json" in fpath:
        with open(fpath, "w") as f:
            _json.dump(data, f)

    else:
        raise (
            NotImplementedError(
                " ".join(
                    [
                        "The save function could not interpret the necessary method",
                        f"to save the file based on the fpath {fpath}. Consider updating",
                        "the function to handle files of this type",
                    ]
                )
            )
        )

    if verbose >= 1:
        print(f"File saved to fpath: {fpath}")
