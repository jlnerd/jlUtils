"""
Operations related to parsing information for files, strings, etc.
"""

import datetime as _datetime


def storeID_cameraID_from_fname(fname):
    """
    Fetch the storeID anf cameraID from a standard filename such as 
    'R216_1578240_01302020_15-45-07UTC.mp4'
    
    Args:
        fname: str. The name of the video of interest
    
    Returns:
        storeID, cameraID: tuple of strings. The store and camera 
            IDs for the filename
    """

    splits = fname.split("_")

    storeID = splits[0]
    cameraID = splits[1]

    return storeID, cameraID


def datetime_from_timestamp(timestamp_str):
    """
    Parse the timestamp string passed to retrieve
    the datetime object
    """

    try:
        timestamp_str = timestamp_str.split("_-_")[0]

        split_strs = ["_", " "]

        for split_str in split_strs:
            if split_str in timestamp_str:
                break

        splits = timestamp_str.split(split_str)

        if len(splits) == 1:
            # assume date is missing
            ymd = "01010001"

        elif len(splits) == 2:
            ymd = splits[0]

        hms = splits[-1]

        # fetch ymd_format_str
        if len(ymd) == 8:
            ymd_format_str = "%m%d%Y"

        # Reformat hms str
        if len(hms.split("-")) == 2:
            # slice off just the first timestamp
            hms = hms.split("-")[0]

        if "AM" in hms or "PM" in hms:
            # Convert to 24hour string
            if hms[-2:] == "AM" and hms[:2] == "12":
                hms = "00" + hms[2:-2]
            # remove the AM
            elif hms[-2:] == "AM":
                hms = hms[:-2]

            # Checking if last two elements of time
            # is PM and first two elements are 12
            elif hms[-2:] == "PM" and hms[:2] == "12":
                hms = hms[:-2]
            else:
                # add 12 to hours and remove PM
                hms = str(int(hms[:2]) + 12) + hms[2:8]

        hms = hms.replace("UTC", "").replace("PM", "").replace("AM", "")

        # fetch hms_format_str
        if "-" in hms:
            hms_format_str = "%H-%M-%S"
        elif len(hms) == 4:
            hms_format_str = "%H%M"
        else:
            hms_format_str = "%H%M%S"

        date_time_str = ymd + split_str + hms

        timestamp = _datetime.datetime.strptime(
            date_time_str, ymd_format_str + split_str + hms_format_str
        )
        timestamp = timestamp.replace(tzinfo=_datetime.timezone.utc)
    except Exception as e:
        if not e.args:
            e.args = ("",)
        e.args = (f"For timestamp_str: {timestamp_str}: " + e.args[0],)
        raise e

    return timestamp
