"""
operations related to importing modules/APIs/libs
"""
import importlib as _importlib
import os as _os
import sys as _sys


def import_from_repo_dir(repo_dir, API_name):
    """
    Force importing from a specific repo directory
    using importlib. This is gaurenteed to function properly,
    unlike the `sys.path.insert(0, repo_dir)` method, which
    will fail to import the module from the new path if the module
    has already been improted previously. For example, when `fuegodata`
    is imported for the first time, it also imports `fuegosecrets` from
    the site-packages path, so even if you add `sys.path.insert(0, repo_dir)`
    and then call `import feugosecrets`, it will still import from the 
    site-packages directory, unless you use this function to import it
    
    Args:
        repo_dir: str. The directory where the API/lib of interest is located
        API_name: str. The name of the API/lib you are importing
        
    Returns:
        API: module: The imported API/lib root module object
    """
    if ".py" not in API_name:
        fpath = _os.path.join(repo_dir, API_name, "__init__.py")
    else:
        fpath = _os.path.join(repo_dir, API_name)

    spec = _importlib.util.spec_from_file_location(API_name, fpath)
    API = _importlib.util.module_from_spec(spec)
    spec.loader.exec_module(API)

    return API
