"""imagedata_transport_s3"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    from importlib.metadata import version
    __version__ = version('imagedata_transport_s3')
except Exception:
    from . import __path__ as _path
    from os.path import isfile, join
    _fname = join(_path[0], "..", "VERSION.txt")
    if not isfile(_fname):
        _fname = join(_path[0], "..", "..", "VERSION.txt")
    if isfile(_fname):
        with open(_fname, 'r') as fh:
            __version__ = fh.readline().strip()
    else:
        __version__ = None

__author__ = 'Erling Andersen, Haukeland University Hospital, Bergen, Norway'
__email__ = 'Erling.Andersen@Helse-Bergen.NO'
