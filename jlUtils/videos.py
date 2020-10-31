"""
Utility functions for interacting with videos
"""
import logging as _logging

import tqdm as _tqdm
import cv2 as _cv2
import matplotlib.pyplot as _plt

_logger = _logging.getLogger("fuegodata")


def create_video_from_imgs(img_fpaths, mp4_fpath, fps=5, sort=True):
    """
    
    Args:
        sort: boolean. Whether or not to sort the img_fpaths list
    """

    _logger.info(f"creating video from {len(img_fpaths)} imgs...")

    if sort:
        img_fpaths = list(sorted(img_fpaths))

    # Fetch dimensions
    img = _plt.imread(img_fpaths[0])
    height, width, layers = img.shape
    size = (width, height)

    out = _cv2.VideoWriter(mp4_fpath, _cv2.VideoWriter_fourcc(*"MP4V"), fps, size)

    try:
        _tqdm.tqdm._instances.clear()
    except:
        pass
    pbar = _tqdm.tqdm(img_fpaths)

    for fpath in img_fpaths:
        pbar.update()
        img = _cv2.imread(fpath)
        out.write(img)

    out.release()
    pbar.close()

    _logger.info(f"!!Finished!! video saved to:\n\t" + mp4_fpath)
