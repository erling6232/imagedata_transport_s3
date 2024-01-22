"""Read/Write image files in S3/Minio storage.
"""
import minio.error
# Copyright (c) 2024 Erling Andersen, Haukeland University Hospital, Bergen, Norway

import os.path
import io
from minio import Minio
import urllib
import logging
import tempfile
import shutil
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
        self.destination = "/".join(root_split[2:]) \
            if len(root_split) > 2 and len(root_split[2]) \
            else None
        self.__mode = mode
        self.__local = False
        self.__must_upload = False
        self.__tmpdir = None
        self.__zipfile = None

        self.client = Minio(
            self.netloc,
            access_key=opts['username'],
            secret_key=opts['password'],
            cert_check=False
        )
        self.bucket = bucket
        try:
            if self.client.bucket_exists(bucket):

                print('Bucket exists')
            else:
                if mode[0] == 'r':
                    raise RootDoesNotExist("Bucket ({}) does not exist".format(bucket))
                else:
                    self.client.make_bucket(bucket)
                print('Bucket "{}" is created'.format(bucket))
        except minio.error.S3Error:
            if mode[0] == 'r':
                raise RootDoesNotExist("Bucket ({}) does not exist".format(bucket))
            else:
                self.client.make_bucket(bucket)
            print('Bucket "{}" is created'.format(bucket))

    def walk(self, top):
        """Generate the file names in a directory tree by walking the tree.
        Input:
        - top: starting point for walk (str)
        Return:
        - tuples of (root, dirs, files)
        """
        raise NotImplementedError('S3Transport.walk is not implemented')

    def isfile(self, path):
        """Return True if path is an existing regular file.
        """
        raise NotImplementedError('S3Transport.isfile is not implemented')

    def open(self, path, mode='r'):
        """Extract a member from the archive as a file-like object.
        """
        if mode[0] == 'r' and not self.__local:
            if len(path) == 0:
                raise FileNotFoundError('Empty filename "{}" not found.'.format(path))
            self.__tmpdir = tempfile.mkdtemp()
            self.__zipfile = os.path.join(self.__tmpdir, path)
            self.client.fget_object(
                bucket_name=self.bucket,
                object_name=path,
                file_path=self.__zipfile
            )
            self.__local = True

        elif mode[0] == 'w' and not self.__local:
            self.__tmpdir = tempfile.mkdtemp()
            self.__zipfile = os.path.join(self.__tmpdir, 'upload.zip')
            self.__local = True
            self.__must_upload = True
            print('Write ', self.__zipfile)
        if self.__local:
            return io.FileIO(self.__zipfile, mode)
        else:
            raise IOError('Could not download bucket "{}"'.format(self.bucket))

    def close(self):
        """Close the transport
        """
        if self.__must_upload:
            # Upload zip file to S3 server
            print('Upload to bucket "{}"'.format(self.bucket))
            logger.debug('Upload to bucket "{}"'.format(self.bucket))
            result = self.client.fput_object(bucket_name=self.bucket,
                                             object_name="newname",
                                             file_path=self.__zipfile,
                                             content_type="application/zip"
                                             )
            print('Upload created {}; etag: {}, version-id: {}'.format(
                result.object_name, result.etag, result.version_id
            ))
            logger.debug('Upload created {}; etag: {}, version-id: {}'.format(
                result.object_name, result.etag, result.version_id
            ))
        if self.__tmpdir is not None:
            shutil.rmtree(self.__tmpdir)

    def info(self, path) -> str:
        """Return info describing the object

        Args:
            path (str): object path

        Returns:
            description (str): Preferably a one-line string describing the object
        """
        raise NotImplementedError('S3Transport.info is not implemented')
