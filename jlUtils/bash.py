"""
Operations for interacting with bash/terminal commands/scripts
"""

import subprocess as _subprocess


def run_command(command):
    """
    Executes a terminal/bash/CLI command passed as a string and returns the outputs or raises an error if the command fails
    
    Args:
        command: string. The command to be executed
        
    Returns:
        output: string. The CLI/terminal/bash output
    """

    try:
        output = _subprocess.check_output(
            command, stderr=_subprocess.STDOUT, shell=True
        ).decode("utf-8")
    except _subprocess.CalledProcessError as e:
        raise ValueError(e.output.decode("utf-8"))

    return output
