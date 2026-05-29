"""imagedata_transport_s3"""

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    from importlib.metadata import version
    __version__ = version('imagedata_transport_s3')
except Exception:
    __version__ = None

__author__ = 'Erling Andersen, Haukeland University Hospital, Bergen, Norway'
__email__ = 'Erling.Andersen@Helse-Bergen.NO'
