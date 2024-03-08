#!/usr/bin/env python3

import unittest
import sys
import os
import os.path
import logging
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
logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG)

host = os.environ.get('MINIO_HOST')
bucket = os.environ.get('MINIO_BUCKET')
access_key = os.environ.get('ACCESS_KEY')
secret_key = os.environ.get('SECRET_KEY')


class TestS3TransportPlugin(unittest.TestCase):
    def setUp(self):
        plugins = imagedata.transports.get_transporter_list()
        self.s3_plugin = None
        for pname, ptype, pclass in plugins:
            if ptype == 's3':
                self.s3_plugin = pclass
        self.assertIsNotNone(self.s3_plugin)
        self.client = Minio(host, access_key, secret_key, cert_check=True)
        self._make_bucket(bucket)
        self.transport = self.s3_plugin(
            netloc=host,
            root='/{}'.format(bucket),
            opts={
                'username': access_key,
                'password': secret_key
            }
        )
        self._delete_bucket()

    def tearDown(self):
        self._delete_bucket()

    def _make_bucket(self, bucket):
        if not self.client.bucket_exists(bucket):
            self.client.make_bucket(bucket)

    def _delete_bucket(self):
        # Remove a prefix recursively.
        delete_object_list = map(
            lambda x: DeleteObject(x.object_name),
            self.client.list_objects(bucket, recursive=True),
        )
        errors = self.client.remove_objects(bucket, delete_object_list)
        try:
            for error in errors:
                logger.error("error occurred when deleting object {}".format(error))
        except S3Error:
            pass

        logger.debug('_delete_bucket: verify bucket: {}'.format(bucket))
        if self.client.bucket_exists(bucket):
            logger.debug('_delete_bucket: Bucket exists')
            self.client.remove_bucket(bucket)
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
        self.assertEqual(
            self.transport.exists('/{}/nofile'.format(bucket)),
            False
        )
        self.assertEqual(
            self.transport.exists('/{}/time00.zip'.format(bucket)),
            True
        )
        logger.debug(self.transport.info('/{}/time00.zip'.format(bucket)))

    def test_isfile(self):
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
        self.assertEqual(
            self.transport.isfile('/{}/time00.zip'.format(bucket)),
            True
        )
        self.assertEqual(
            self.transport.isfile('/{}/nofile'.format(bucket)),
            False
        )

    def test_walk(self):
        # Ensure bucket exists
        d = 's3://{}:{}@{}/{}/'.format(
            access_key,
            secret_key,
            host,
            bucket
        )
        si1 = Series(os.path.join('data', 'time00', 'Image_00019.dcm'))
        si1.write(d + 't/time00.zip', formats=['dicom'])
        si1.write(d + 'u/time00.zip', formats=['dicom'])
        si1.write(d + 't/0/time00.zip', formats=['dicom'])
        si1.write(d + 't/1/time00.zip', formats=['dicom'])
        si2 = Series(os.path.join('data', 'time00', 'Image_00020.dcm'))
        si2.write(d + 't/time01.zip', formats=['dicom'])
        si2.write(d + 'u/time01.zip', formats=['dicom'])
        # Now ask for non-existing and existing file
        # transport = S3Transport(
        #     netloc=host,
        #     root='/{}'.format(bucket),
        #     opts={
        #         'username': access_key,
        #         'password': secret_key
        #     }
        # )
        logger.debug('walk: ' + bucket)
        # for root, dirs, files in transport.walk('/{}/'.format(bucket)):
        #     pass
        # print('walk:', bucket + '/t/')
        # transport.walk('/{}/{}'.format(bucket, 't/'))
        top = '/{}/{}'.format(bucket, 't/')
        logger.debug('walk: self.transport: {}'.format(self.transport))
        logger.debug('walk: self.transport.walk: {}'.format(self.transport.walk))
        logger.debug('walk: calling self.transport.walk({})'.format(top))
        walk_list = self.transport.walk(top)
        for root, dirs, files in walk_list:
            logger.debug('Found: {} {} {}'.format(root, dirs, files))
        logger.debug('walk: returned from self.transport.walk')
        # self.assertEqual(
        #     transport.isfile('/{}/time00.zip'.format(bucket)),
        #     True
        # )
        # raise ValueError("stop")

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
