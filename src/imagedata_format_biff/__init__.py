"""imagedata_format_biff"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    from importlib.metadata import version
    __version__ = version('imagedata_format_biff')
except ModuleNotFoundError:
    from importlib_metadata import version
    __version__ = version('imagedata_format_biff')
except Exception:
    # import imagedata as _
    from . import __path__ as _path
    from os.path import join
    with open(join(_path[0], "..", "VERSION.txt"), 'r') as fh:
        __version__ = fh.readline().strip()

__author__ = 'Erling Andersen, Haukeland University Hospital, Bergen, Norway'
__email__ = 'Erling.Andersen@Helse-Bergen.NO'
