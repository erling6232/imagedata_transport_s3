#!/usr/bin/env python3

import unittest
import sys
import os.path
# import numpy as np
# import logging
# import argparse
# import tempfile
#from .context import imagedata
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

# import mimetypes
# mimetypes.add_type('application/biff', '.biff')

class TestS3TransportPlugin(unittest.TestCase):
    def setUp(self):
        plugins = imagedata.transports.get_transporter_list()
        self.s3_plugin = None
        for pname, ptype, pclass in plugins:
            if ptype == 's3':
                self.s3_plugin = pclass
        self.assertIsNotNone(self.s3_plugin)

    def test_write_single_file(self):
        si1 = Series(os.path.join('data', 'time00', 'Image_00019.dcm'))
        host = 'play.min.io:9443'
        access_key = 'Q3AM3UQ867SPQQA43P2F'
        secret_key = 'zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG'
        bucket = 'imagedata-transport-s3'
        # bucket = 'my-bucketname'
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
