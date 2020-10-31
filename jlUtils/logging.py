"""
Utility functions related to logging operations
"""
import logging as _logging
import os as _os

from fuegodata import paths as _paths

LOGGER_NAME = "fuegodata"

LOGS_DIR = _paths.logs_dir


def setupLogger(name, logs_dir, init=False):
    """
    get the unified logging logger object
    If the logger has already been already initialized, returns the reference to the existing logger.
    
    Args:
        name: string. The name for the logger
        logs_dir: string. The path to where the .log file is saved
        init: boolean. Whether or not this is the first time the logger is initialized
        
    Returns:
        logger: the setup logger.
    """

    # Make sure the logging directory exists
    if not _os.path.exists(logs_dir):
        _os.makedirs(str(logs_dir))

    log_fpath = _os.path.join(logs_dir, name + ".log")

    logger = _logging.getLogger(name)

    logger.handlers.clear()

    logger.setLevel(_logging.DEBUG)
    logger.file = log_fpath

    fh = _logging.FileHandler(log_fpath)
    fh.setLevel(_logging.DEBUG)

    # console handler also on DEBUG level
    sh = _logging.StreamHandler()
    sh.setLevel(_logging.DEBUG)

    # try to fetch a version number
    init_fpath = logs_dir.split(name)[0] + name
    init_fpath = _os.path.join(init_fpath, "__init__.py")
    if _os.path.exists(init_fpath):
        with open(init_fpath, "r") as f:
            init_str = f.read()
        if "__version__" in init_str:
            version = init_str.split("__version__ = ")[-1]
            version = version.split("\n")[0]
            version = "v" + version.replace('"', "")
        else:
            version = "v0.0.0"
    else:
        version = "v0.0.0"

    # log formatter
    class PathToModuleFilter(_logging.Filter):
        """
        Custom logging filter which reformats the 
        `pathname` arg into the more terse API module path.
        """

        def filter(self, record):
            fpath = record.pathname
            fpath = fpath.split(name)[-1]
            fpath = name + ":" + version + "." + fpath
            fpath = fpath.replace("/", ".").replace(".py", "")
            record.pathname = fpath
            return True

    logger.addFilter(PathToModuleFilter())

    formatter = _logging.Formatter(
        "[PID:%(process)d][%(asctime)s][%(levelname)s][%(pathname)s.%(funcName)s:%(lineno)s] %(message)s"
    )
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(sh)

    if init:
        logger.info("Logging basicConfig set and logging started")
        logger.info(f"Logs saved to: {log_fpath}")

    return logger


def process_tag(__file__value, fxn_name=None, API_dir=str(_paths.API_dir)):
    """
    Build that standard process_tag logging tag to be added to a
    loggers.info() statement
    
    Args:
        __file__value: the __file__ value for a given module (i.e. the filepath)
        fxn_name: None or string. If None, only the module tag will be generated, otherswise {module.function} will be generated
        
    Returns:
        module_fxn_tag: string. the module.function tag
    """

    __file__value = _os.path.abspath(__file__value)

    module_fxn_tag = "[" + _os.path.splitext(__file__value.replace(API_dir, "")[1:])[
        0
    ].replace("/", ".")

    if fxn_name is not None:
        module_fxn_tag += f".{fxn_name}"

    module_fxn_tag += "] "

    return module_fxn_tag


setupLogger(name=LOGGER_NAME, logs_dir=LOGS_DIR)
LOGGER = _logging.getLogger(LOGGER_NAME)
LOGGER.propagate = False  # Supress duplicate logs
