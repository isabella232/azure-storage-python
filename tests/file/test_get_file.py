﻿# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------
import base64
import os
import unittest

from azure.storage.file import (
    File,
    FileService,
    DeleteSnapshot,
)
from tests.testcase import (
    StorageTestCase,
    TestMode,
    record,
)

# ------------------------------------------------------------------------------
TEST_FILE_PREFIX = 'file'
FILE_PATH = 'file_output.temp.dat'


# ------------------------------------------------------------------------------

class StorageGetFileTest(StorageTestCase):
    def setUp(self):
        super(StorageGetFileTest, self).setUp()

        self.fs = self._create_storage_service(FileService, self.settings)

        self.share_name = self.get_resource_name('utshare')
        self.directory_name = self.get_resource_name('utdir')

        if not self.is_playback():
            self.fs.create_share(self.share_name)
            self.fs.create_directory(self.share_name, self.directory_name)

        self.byte_file = self.get_resource_name('bytefile')
        self.byte_data = self.get_random_bytes(64 * 1024 + 5)

        if not self.is_playback():
            self.fs.create_file_from_bytes(self.share_name, self.directory_name, self.byte_file, self.byte_data)

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.fs.MAX_SINGLE_GET_SIZE = 32 * 1024
        self.fs.MAX_CHUNK_GET_SIZE = 4 * 1024

    def tearDown(self):
        if not self.is_playback():
            try:
                self.fs.delete_share(self.share_name, delete_snapshots=DeleteSnapshot.Include)
            except:
                pass

        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

        return super(StorageGetFileTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    def _get_file_reference(self):
        return self.get_resource_name(TEST_FILE_PREFIX)

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    # -- Get test cases for files ----------------------------------------------

    @record
    def test_unicode_get_file_unicode_data(self):
        # Arrange
        file_data = u'hello world啊齄丂狛狜'.encode('utf-8')
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, file_name)

        # Assert
        self.assertIsInstance(file, File)
        self.assertEqual(file.content, file_data)

    @record
    def test_unicode_get_file_binary_data(self):
        # Arrange
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)

        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, binary_data)

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, file_name)

        # Assert
        self.assertIsInstance(file, File)
        self.assertEqual(file.content, binary_data)

    @record
    def test_get_file_no_content(self):
        # Arrange
        file_data = b''
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, file_name)

        # Assert
        self.assertEqual(file_data, file.content)
        self.assertEqual(0, file.properties.content_length)

    def test_get_file_to_bytes(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, self.byte_file)

        # Assert
        self.assertEqual(self.byte_data, file.content)

    def test_get_file_to_bytes_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, self.byte_file,
                                         progress_callback=callback)

        # Assert
        self.assertEqual(self.byte_data, file.content)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_file_to_bytes_non_parallel(self):
        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, self.byte_file, max_connections=1,
                                         progress_callback=callback)

        # Assert
        self.assertEqual(self.byte_data, file.content)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress, single_download=True)

    @record
    def test_get_file_to_bytes_small(self):
        # Arrange
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, file_name, progress_callback=callback)

        # Assert
        self.assertEqual(file_data, file.content)
        self.assert_download_progress(len(file_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_file_to_stream(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(self.share_name, self.directory_name, self.byte_file, stream)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_file_to_stream_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(
                self.share_name, self.directory_name, self.byte_file, stream, progress_callback=callback)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_file_to_stream_non_parallel(self):
        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(
                self.share_name, self.directory_name, self.byte_file, stream, max_connections=1,
                progress_callback=callback)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress, single_download=True)

    @record
    def test_get_file_to_stream_small(self):
        # Arrange
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(self.share_name, self.directory_name, file_name, stream,
                                              progress_callback=callback)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data, actual)
        self.assert_download_progress(len(file_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_file_to_stream_from_snapshot(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        # Create a snapshot of the share and delete the file
        share_snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.delete_file(self.share_name, self.directory_name, self.byte_file)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(self.share_name, self.directory_name,
                                              self.byte_file, stream, snapshot=share_snapshot.snapshot)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_file_to_stream_with_progress_from_snapshot(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        # Create a snapshot of the share and delete the file
        share_snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.delete_file(self.share_name, self.directory_name, self.byte_file)
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(
                self.share_name, self.directory_name,
                self.byte_file, stream, progress_callback=callback, snapshot=share_snapshot.snapshot)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_file_to_stream_non_parallel_from_snapshot(self):
        # Arrange
        # Create a snapshot of the share and delete the file
        share_snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.delete_file(self.share_name, self.directory_name, self.byte_file)
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(
                self.share_name, self.directory_name, self.byte_file, stream, max_connections=1,
                progress_callback=callback, snapshot=share_snapshot.snapshot)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress, single_download=True)

    @record
    def test_get_file_to_stream_small_from_snapshot(self):
        # Arrange
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        # Create a snapshot of the share and delete the file
        share_snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.delete_file(self.share_name, self.directory_name, file_name)
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        with open(FILE_PATH, 'wb') as stream:
            file = self.fs.get_file_to_stream(self.share_name, self.directory_name, file_name, stream,
                                              progress_callback=callback, snapshot=share_snapshot.snapshot)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data, actual)
        self.assert_download_progress(len(file_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_file_to_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, self.byte_file, FILE_PATH)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_file_to_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_path(
            self.share_name, self.directory_name, self.byte_file, FILE_PATH, progress_callback=callback)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress)

    @record
    def test_get_file_to_path_non_parallel(self):
        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_path(
            self.share_name, self.directory_name, self.byte_file, FILE_PATH,
            progress_callback=callback, max_connections=1)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress, single_download=True)

    @record
    def test_get_file_to_path_small(self):
        # Arrange
        file_data = self.get_random_bytes(1024)
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, file_name, FILE_PATH,
                                        progress_callback=callback)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data, actual)
        self.assert_download_progress(len(file_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    def test_ranged_get_file_to_path(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        end_range = self.fs.MAX_SINGLE_GET_SIZE + 1024
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, self.byte_file, FILE_PATH,
                                        start_range=1, end_range=end_range)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:end_range + 1], actual)

    def test_ranged_get_file_to_path_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        start_range = 3
        end_range = self.fs.MAX_SINGLE_GET_SIZE + 1024
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, self.byte_file, FILE_PATH,
                                        start_range=start_range, end_range=end_range,
                                        progress_callback=callback)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[start_range:end_range + 1], actual)
        self.assert_download_progress(end_range - start_range + 1, self.fs.MAX_CHUNK_GET_SIZE,
                                      self.fs.MAX_SINGLE_GET_SIZE, progress)

    @record
    def test_ranged_get_file_to_path_small(self):
        # Arrange

        # Act
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, self.byte_file, FILE_PATH,
                                        start_range=1, end_range=4)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:5], actual)

    @record
    def test_ranged_get_file_to_path_non_parallel(self):
        # Arrange

        # Act
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, self.byte_file, FILE_PATH,
                                        start_range=1, end_range=3, max_connections=1)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data[1:4], actual)

    @record
    def test_ranged_get_file_to_path_invalid_range_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        file_size = self.fs.MAX_SINGLE_GET_SIZE + 1
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        # Act
        end_range = 2 * self.fs.MAX_SINGLE_GET_SIZE
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, file_name, FILE_PATH,
                                        start_range=1, end_range=end_range)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data[1:file_size], actual)

    @record
    def test_ranged_get_file_to_path_invalid_range_non_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        file_size = 1024
        file_data = self.get_random_bytes(file_size)
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, file_data)

        # Act
        end_range = 2 * self.fs.MAX_SINGLE_GET_SIZE
        file = self.fs.get_file_to_path(self.share_name, self.directory_name, file_name, FILE_PATH,
                                        start_range=1, end_range=end_range)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(file_data[1:file_size], actual)

    def test_get_file_to_path_with_mode(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        with open(FILE_PATH, 'wb') as stream:
            stream.write(b'abcdef')

        # Act

        # Assert
        with self.assertRaises(BaseException):
            file = self.fs.get_file_to_path(self.share_name, self.directory_name, self.byte_file, FILE_PATH, 'a+b')

    def test_get_file_to_path_with_mode_non_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        with open(FILE_PATH, 'wb') as stream:
            stream.write(b'abcdef')

        # Act
        file = self.fs.get_file_to_path(
            self.share_name, self.directory_name, self.byte_file, FILE_PATH, 'a+b', max_connections=1)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(b'abcdef' + self.byte_data, actual)

    def test_get_file_to_text(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.fs.MAX_SINGLE_GET_SIZE + 1)
        self.fs.create_file_from_text(self.share_name, self.directory_name, text_file, text_data)

        # Act
        file = self.fs.get_file_to_text(self.share_name, self.directory_name, text_file)

        # Assert
        self.assertEqual(text_data, file.content)

    def test_get_file_to_text_with_progress(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        text_file = self.get_resource_name('textfile')
        text_data = self.get_random_text_data(self.fs.MAX_SINGLE_GET_SIZE + 1)
        self.fs.create_file_from_text(self.share_name, self.directory_name, text_file, text_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_text(self.share_name, self.directory_name, text_file, progress_callback=callback)

        # Assert
        self.assertEqual(text_data, file.content)
        self.assert_download_progress(len(text_data.encode('utf-8')), self.fs.MAX_CHUNK_GET_SIZE,
                                      self.fs.MAX_SINGLE_GET_SIZE, progress)

    @record
    def test_get_file_to_text_non_parallel(self):
        # Arrange
        text_file = self._get_file_reference()
        text_data = self.get_random_text_data(self.fs.MAX_SINGLE_GET_SIZE + 1)
        self.fs.create_file_from_text(self.share_name, self.directory_name, text_file, text_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_text(self.share_name, self.directory_name, text_file, max_connections=1,
                                        progress_callback=callback)

        # Assert
        self.assertEqual(text_data, file.content)
        self.assert_download_progress(len(self.byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE,
                                      progress, single_download=True)

    @record
    def test_get_file_to_text_small(self):
        # Arrange
        file_data = self.get_random_text_data(1024)
        file_name = self._get_file_reference()
        self.fs.create_file_from_text(self.share_name, self.directory_name, file_name, file_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_text(self.share_name, self.directory_name, file_name, progress_callback=callback)

        # Assert
        self.assertEqual(file_data, file.content)
        self.assert_download_progress(len(file_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    @record
    def test_get_file_to_text_with_encoding(self):
        # Arrange
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, data)

        # Act
        file = self.fs.get_file_to_text(self.share_name, self.directory_name, file_name, 'utf-16')

        # Assert
        self.assertEqual(text, file.content)

    @record
    def test_get_file_to_text_with_encoding_and_progress(self):
        # Arrange
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_name = self._get_file_reference()
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, data)

        # Act
        progress = []

        def callback(current, total):
            progress.append((current, total))

        file = self.fs.get_file_to_text(
            self.share_name, self.directory_name, file_name, 'utf-16', progress_callback=callback)

        # Assert
        self.assertEqual(text, file.content)
        self.assert_download_progress(len(data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_file_non_seekable(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)
            file = self.fs.get_file_to_stream(self.share_name, self.directory_name, self.byte_file, non_seekable_stream,
                                              max_connections=1)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_file_non_seekable_parallel(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)

            with self.assertRaises(BaseException):
                file = self.fs.get_file_to_stream(
                    self.share_name, self.directory_name, self.byte_file, non_seekable_stream)

                # Assert

    def test_get_file_non_seekable_from_snapshot(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        # Create a snapshot of the share and delete the file
        share_snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.delete_file(self.share_name, self.directory_name, self.byte_file)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)
            file = self.fs.get_file_to_stream(self.share_name, self.directory_name, self.byte_file, non_seekable_stream,
                                              max_connections=1, snapshot=share_snapshot.snapshot)

        # Assert
        self.assertIsInstance(file, File)
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(self.byte_data, actual)

    def test_get_file_non_seekable_parallel_from_snapshot(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        # Create a snapshot of the share and delete the file
        share_snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.delete_file(self.share_name, self.directory_name, self.byte_file)

        # Act
        with open(FILE_PATH, 'wb') as stream:
            non_seekable_stream = StorageGetFileTest.NonSeekableFile(stream)

            with self.assertRaises(BaseException):
                self.fs.get_file_to_stream(
                    self.share_name, self.directory_name,
                    self.byte_file, non_seekable_stream, snapshot=share_snapshot.snapshot)


    @record
    def test_get_file_exact_get_size(self):
        # Arrange
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.fs.MAX_SINGLE_GET_SIZE)
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, byte_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, file_name, progress_callback=callback)

        # Assert
        self.assertEqual(byte_data, file.content)
        self.assert_download_progress(len(byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_file_exact_chunk_size(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        file_name = self._get_file_reference()
        byte_data = self.get_random_bytes(self.fs.MAX_SINGLE_GET_SIZE + self.fs.MAX_CHUNK_GET_SIZE)
        self.fs.create_file_from_bytes(self.share_name, self.directory_name, file_name, byte_data)

        progress = []

        def callback(current, total):
            progress.append((current, total))

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, file_name, progress_callback=callback)

        # Assert
        self.assertEqual(byte_data, file.content)
        self.assert_download_progress(len(byte_data), self.fs.MAX_CHUNK_GET_SIZE, self.fs.MAX_SINGLE_GET_SIZE, progress)

    def test_get_file_with_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        # Arrange

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, self.byte_file, validate_content=True)

        # Assert
        self.assertEqual(self.byte_data, file.content)

    def test_get_file_range_with_md5(self):
        # parallel tests introduce random order of requests, can only run live
        if TestMode.need_recording_file(self.test_mode):
            return

        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, self.byte_file, start_range=0,
                                         end_range=1024, validate_content=True)

        # Assert
        self.assertFalse(hasattr(file.properties.content_settings, 'content_md5'))

        # Arrange
        props = self.fs.get_file_properties(self.share_name, self.directory_name, self.byte_file)
        props.properties.content_settings.content_md5 = 'MDAwMDAwMDA='
        self.fs.set_file_properties(self.share_name, self.directory_name, self.byte_file,
                                    props.properties.content_settings)

        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, self.byte_file, start_range=0,
                                         end_range=1024, validate_content=True)

        # Assert
        self.assertEqual('MDAwMDAwMDA=', file.properties.content_settings.content_md5)

    @record
    def test_get_file_server_encryption(self):
        # Act
        file = self.fs.get_file_to_bytes(self.share_name, self.directory_name, self.byte_file, start_range=0,
                                         end_range=1024, validate_content=True)
        # Assert
        if self.is_file_encryption_enabled():
            self.assertTrue(file.properties.server_encrypted)
        else:
            self.assertFalse(file.properties.server_encrypted)

    @record
    def test_get_file_properties_server_encryption(self):
        # Act
        props = self.fs.get_file_properties(self.share_name, self.directory_name, self.byte_file)

        # Assert
        if self.is_file_encryption_enabled():
            self.assertTrue(props.properties.server_encrypted)
        else:
            self.assertFalse(props.properties.server_encrypted)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
