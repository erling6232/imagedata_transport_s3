"""Read/Write image files in S3/Minio storage.
"""

# Copyright (c) 2024 Erling Andersen, Haukeland University Hospital, Bergen, Norway

import os.path
from minio import Minio
import urllib
import logging
# import struct
# import numpy as np
#
# import imagedata.formats
# import imagedata.axis
from imagedata.transports.abstracttransport import AbstractTransport
from imagedata.transports import RootDoesNotExist

logger = logging.getLogger(__name__)


class PixelTypeNotSupported(Exception):
    """Thrown when pixel type is not supported.
    """
    pass


class VaryingImageSize(Exception):
    """Thrown when the bands are of varying size.
    """
    pass


class NoBands(Exception):
    """Thrown when no bands are defined.
    """
    pass


class BadShapeGiven(Exception):
    """Thrown when input_shape is not like (t)x(z).
    """
    pass


class S3Transport(AbstractTransport):
    """Read/write from S3/Minio storage.
    """

    name = "s3"
    description = "Read and write from S3/Minio storage."
    authors = "Erling Andersen"
    version = "1.0.0"
    url = "www.helse-bergen.no"
    schemes = ["s3"]

    def __init__(self, netloc=None, root=None, mode='r', read_directory_only=False, opts=None):
        super(S3Transport, self).__init__(self.name, self.description,
                                          self.authors, self.version, self.url, self.schemes)
        # self.client = Minio(
        #     "play.min.io",
        #     access_key="Q3AM3UQ867SPQQA43P2F",
        #     secret_key="zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
        #     cert_check=False
        # )
        # if self.client.bucket_exists("imagedata_transport_s3"):
        #     print('Bucket exists')
        # else:
        #     print('Bucket do not exist')
        if opts is None:
            opts = {}
        self.read_directory_only = read_directory_only
        self.opts = opts
        # Does netloc include username and password?
        if '@' in netloc:
            # Add fake scheme to satisfy urlsplit()
            url_tuple = urllib.parse.urlsplit('s3://' + netloc)
            self.netloc = url_tuple.hostname
            try:
                opts['username'] = url_tuple.username
            except AttributeError:
                opts['username'] = None
            try:
                opts['password'] = url_tuple.password
            except AttributeError:
                opts['password'] = None
        else:
            self.netloc = netloc
        logger.debug("XnatTransport __init__ root: {}".format(root))
        root_split = root.split('/')
        try:
            bucket = root_split[1]
        except IndexError:
            raise ValueError('No bucket given in URL {}'.format(root))
        destination = "/".join(root_split[2:]) if len(root_split) > 2 and len(root_split[2]) else None
        self.__mode = mode
        self.__local = False
        self.__must_upload = False
        self.__tmpdir = None

        self.client = Minio(
            self.netloc,
            access_key=opts['username'],
            secret_key=opts['password'],
            cert_check=False
        )
        if self.client.bucket_exists(bucket):

            print('Bucket exists')
        else:
            if mode[0] == 'r':
                raise RootDoesNotExist("Bucket ({}) does not exist".format(bucket))
                raise
            print('Bucket do not exist')

    def walk(self, top):
        """Generate the file names in a directory tree by walking the tree.
        Input:
        - top: starting point for walk (str)
        Return:
        - tuples of (root, dirs, files)
        """
        pass

    def isfile(self, path):
        """Return True if path is an existing regular file.
        """
        pass

    def open(self, path, mode='r'):
        """Extract a member from the archive as a file-like object.
        """
        pass

    def close(self):
        """Close the transport
        """
        pass

    def info(self, path) -> str:
        """Return info describing the object

        Args:
            path (str): object path

        Returns:
            description (str): Preferably a one-line string describing the object
        """
        pass
