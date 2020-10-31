"""
Operations related to managing versions
"""


def increment_version(current_version, version_increment="1.0.0"):
    """
    Update the passed version string/number by the specified 
    version increment to generate a new version number

    Args:
        current_version: str. The current version (i.e. `1.0.1`)
        version_increment: str. how much the current version will be
            incremented (i.e. `1.0.0`, `0.1.0`, `0.0.1`)

    Returns:
        new_version: str. The incremented version
    """
    new_version = []
    for current, increment in zip(
        current_version.split("."), version_increment.split(".")
    ):
        new_version.append(str(int(current) + int(increment)))
        if increment == "1":
            break
    # append 0's for new major or minor versions
    if len(new_version) == 1:
        new_version += ["0", "0"]
    elif len(new_version) == 2:
        new_version += ["0"]

    new_version = ".".join(new_version)
    return new_version
