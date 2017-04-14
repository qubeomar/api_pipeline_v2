#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class TestArtifactsModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_artifacts_model(self):
        from qube.src.models.artifacts import Artifacts
        artifacts_data = Artifacts()
        artifacts_data.tenantId = "23432523452345"
        artifacts_data.orgId = "987656789765670"
        artifacts_data.createdBy = "test"
        artifacts_data.projectId = "123457"
        artifacts_data.iterationId = "45678"
        artifacts_data.title = "Test Results"
        artifacts_data.url =\
            "/api/v1/projects/58c1cac14f05a800480c3a8c/2/summary/test"
        artifacts_data.type = "test"
        artifacts_data.contentType = "html"
        artifacts_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            artifacts_data.save()
            self.assertIsNotNone(artifacts_data.mongo_id)
            artifacts_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
