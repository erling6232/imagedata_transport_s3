#!/usr/bin/env python3

import unittest
import sys
import os.path
import logging
import numpy as np
from minio import Minio
from minio.deleteobjects import DeleteObject
from minio.error import S3Error
import imagedata.cmdline
import imagedata.readdata
import imagedata.transports
from imagedata.series import Series

from imagedata import plugins
sys.path.append(os.path.abspath('../src'))
from src.imagedata_transport_s3.s3transport import S3Transport
plugin_type = 'transport'
plugin_name = S3Transport.name + 'transport'
class_name = S3Transport.name
pclass = S3Transport
plugins[plugin_type].append((plugin_name, class_name, pclass))

logger = logging.getLogger(__name__)

# import mimetypes
# mimetypes.add_type('application/biff', '.biff')

host = 'play.min.io:9000'
access_key = 'Q3AM3UQ867SPQQA43P2F'
secret_key = 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'
bucket = 'imagedata-transport-s3'


class TestS3TransportPlugin(unittest.TestCase):
    def setUp(self):
        plugins = imagedata.transports.get_transporter_list()
        self.s3_plugin = None
        for pname, ptype, pclass in plugins:
            if ptype == 's3':
                self.s3_plugin = pclass
        self.assertIsNotNone(self.s3_plugin)
        self._delete_bucket()

    def tearDown(self):
        self._delete_bucket()

    def _delete_bucket(self):
        client = Minio(host, access_key, secret_key, cert_check=True)

        # Remove a prefix recursively.
        delete_object_list = map(
            lambda x: DeleteObject(x.object_name),
            client.list_objects(bucket, recursive=True),
        )
        errors = client.remove_objects(bucket, delete_object_list)
        try:
            for error in errors:
                logger.error("error occurred when deleting object {}".format(error))
        except S3Error:
            pass

        logger.debug('_delete_bucket: verify bucket: {}'.format(bucket))
        if client.bucket_exists(bucket):
            logger.debug('_delete_bucket: Bucket exists')
            client.remove_bucket(bucket)
        else:
            logger.debug('_delete_bucket: Bucket does not exist')

    def test_file_exist(self):
        # Ensure bucket exists
        si = Series(os.path.join('data', 'time00', 'Image_00019.dcm'))
        d = 's3://{}:{}@{}/{}/time00.zip'.format(
            access_key,
            secret_key,
            host,
            bucket
        )
        si.write(d, formats=['dicom'])
        # Now ask for non-existing and existing file
        transport = S3Transport(
            netloc=host,
            root='/{}'.format(bucket),
            opts={
                'username': access_key,
                'password': secret_key
            }
        )
        self.assertEqual(
            transport.exists('/{}/nofile'.format(bucket)),
            False
        )
        self.assertEqual(
            transport.exists('/{}/time00.zip'.format(bucket)),
            True
        )

    def test_write_reread_single_file(self):
        si1 = Series(os.path.join('data', 'time00', 'Image_00019.dcm'))
        d = 's3://{}:{}@{}/{}/time00.zip'.format(
            access_key,
            secret_key,
            host,
            bucket
        )
        si1.write(d, formats=['dicom'])
        si2 = Series(d)
        self.assertEqual(si1.dtype, si2.dtype)
        self.assertEqual(si1.shape, si2.shape)


if __name__ == '__main__':
    unittest.main()
