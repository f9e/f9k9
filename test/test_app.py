import os
import tempfile
import unittest
import json

# import pytest

from f9k9.app import app
from f9k9.app import init

class AppTestCase(unittest.TestCase):
    def setUp(self):
        init()
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_formats(self):

        from f9k9.app import prepare_data_array
        from f9k9.app import allowed_file
        import numpy as np

        w, h, c = 150, 150, 3

        static_files = os.listdir('./static/')
        for f in static_files:
            print('testing ' + f)
            if allowed_file(f):
                filename = 'static/' + f

                with open(filename, 'br') as file:
                    rv = prepare_data_array(file=file,
                                            width=w,
                                            height=h,
                                            num_channels=c,
                                            )

                    self.assertEqual(rv.dtype, np.dtype('float32'))
                    self.assertEqual(rv.ndim, 4)
                    self.assertLessEqual(rv.max(), 1.0)
                    self.assertEqual(rv.size, w * h * c)



if __name__ == '__main__':
    unittest.main()
