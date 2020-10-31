"""
General utility functions for interacting with zip files
"""
from zipfile import ZipFile as _ZipFile
import os as _os
import shutil as _shutil


def unzip_file(path_file, extract_dir=None, delete_zip_file=True):
    """
    unzip a single zip file, placing the contents in the specificed extract_dir directory path
    
    Args:
        path_file: string. The path to the zip file of interest
        extract_dir: string. The path to the directory where the unzipped data will be exported
            - If None, the data will be unzipped in the same directory as the zip file
        delete_zip_file: boolean. Whether or not to delete the zip file after
            the contents has been unzipped
        
    Returns:
        path_unzipped_dir: str. The path for the unzipped directory
    """
    if extract_dir == None:
        extract_dir = _os.path.splitext(path_file)[0]
    else:
        if not _os.path.isdir(extract_dir):
            _os.makedirs(extract_dir)

    with _ZipFile(path_file, "r") as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall(extract_dir)
    if delete_zip_file:
        _os.remove(path_file)

    path_unzipped_dir = path_file.replace(".zip", "")
    return path_unzipped_dir


def unzip_files_in_dir(path_dir, verbose=1, delete_zips=True):
    """
    Unzip all the zip files in the specified directory
    
    Args:
        path_dir: string. The path to the directory where zip files are stored
        verbose: int. print-out verbosity
        delete_zips: boolean. Whether or not to delete the zip files after unzipping
        
    Returns:
        None. All files will be unzipped
    """
    for dirname, dirfolders, filenames in _os.walk(path_dir):
        for file in filenames:

            if "zip" in file.lower():
                if verbose >= 1:
                    print("unzipping:", file)

                path_file = _os.path.join(dirname, file)
                unzip_file(path_file, delete_zip_file=delete_zips)


def zip_dir(path_dir):
    """
    Zip the contents of a directory. The generated zip file will have the 
    same path and name as the directory zipped
    
    Args:
        path_dir: string. The path to the directory 
            where zip files are stored
    
    Returns:
        zip_fpath: str. The path to the zip file created
    """

    _shutil.make_archive(path_dir, "zip", path_dir)

    zip_fpath = path_dir + ".zip"

    return zip_fpath
