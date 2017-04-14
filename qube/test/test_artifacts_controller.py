#!/usr/bin/python
"""
Add docstring here
"""
import io
import json
import os
import time
import unittest

from mock import patch
import mongomock
from mongomock import ObjectId

from qube.src.commons.utils import clean_nonserializable_attributes

# noinspection PyUnresolvedReferences
ARTIFACT_URL_WITH_ID = "/v2/pipelines/{}/{}/artifacts/{}"
ARTIFACT_URL = "/v2/pipelines/{}/{}/artifacts"
ITERATION_ID = "891011"

PROJECT_ID = "123456"
SOME_OTHER_PROJECT_ID = "456789"
with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['ARTIFACTS_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['ARTIFACTS_MONGOALCHEMY_SERVER'] = ''
    os.environ['ARTIFACTS_MONGOALCHEMY_PORT'] = ''
    os.environ['ARTIFACTS_MONGOALCHEMY_DATABASE'] = ''
    from qube.src.api.app import app
    from qube.src.models.artifacts import Artifacts


def auth_response():
    userinfo = {
        'id': '1009009009988',
        'type': 'org',
        'tenant': {
            'id': '23432523452345',
            'name': 'tenantname',
            'orgs': [{
                'id': '987656789765670',
                'name': 'orgname'
            }]
        },
        'is_system_user': False
    }
    return json.dumps(userinfo)


def system_user_auth_response():
    userinfo = {
        'id': '1009009009988',
        'type': 'org',
        'tenant': {
            'id': '23432523452345',
            'name': 'tenantname',
            'orgs': [{
                'id': '987656789765670',
                'name': 'orgname'

            }]
        },
        'is_system_user': True
    }
    return json.dumps(userinfo)


def invalid_auth_response():
    userinfo = {
        'id': '1009009009988',
        'type': 'master',
        'tenant': {
            'id': '23432523452345',
            'name': 'tenantname',
            'orgs': [{
                'id': '987656789765670',
                'name': 'orgname'
            }]
        },
        'is_system_user': False
    }
    return json.dumps(userinfo)


def no_auth_response():
    userinfo = {
    }

    return json.dumps(userinfo)


class TestArtifactsController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    def createTestModelData(self):
        return {
            'type': 'test123123124',
            'contentType': 'html',
            'title': 'test',
            'url': 'test'
        }

    def createTestHeaders(self, data):
        headers = [('Content-Type', 'application/json'),
                   ('Authorization',
                    'Bearer authorizationmockedvaluedoesntmatter')]
        if data is not None:
            json_data = json.dumps(data)
            json_data_length = len(json_data)
            headers.append(('Content-Length', str(json_data_length)))
        return headers

    @patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, model, project_id, iteration_id):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            data = Artifacts()
            for key in model:
                data.__setattr__(key, model[key])
            data.projectId = project_id
            data.iterationId = iteration_id
            data.tenantId = "23432523452345"
            data.orgId = "987656789765670"
            data.createdBy = "1009009009988"
            data.modifiedBy = "1009009009988"
            data.createDate = str(int(time.time()))
            data.modifiedDate = str(int(time.time()))
            data.save()
            return data

    @patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        self.model_data = self.createTestModelData()
        self.data = self.setupDatabaseRecords(self.model_data, PROJECT_ID,
                                              ITERATION_ID)
        self.headers = self.createTestHeaders(self.model_data)
        self.auth = auth_response()
        self.test_client = app.test_client()

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.data.remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_post_artifacts(self, *args, **kwargs):
        ist = io.BytesIO(json.dumps(self.model_data).encode('utf-8'))
        rv = self.test_client.post(ARTIFACT_URL.format(PROJECT_ID,
                                                       ITERATION_ID),
                                   input_stream=ist, headers=self.headers)
        result = json.loads(rv.data.decode('utf-8'))

        self.assertTrue(rv._status_code == 201)
        Artifacts.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_put_artifacts_item(self, *args, **kwargs):
        entity_id = str(self.data.mongo_id)
        self.model_data['title'] = 'updated model desc'
        ist = io.BytesIO(json.dumps(self.model_data).encode('utf-8'))
        rv = self.test_client.put(
            ARTIFACT_URL_WITH_ID.format(PROJECT_ID, ITERATION_ID, entity_id),
            input_stream=ist, headers=self.headers)

        self.assertTrue(rv._status_code == 204)
        updated_record = Artifacts.query.get(entity_id)
        self.assertEquals(self.model_data['title'],
                          updated_record.title)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_put_artifacts_item_non_found(self, *args, **kwargs):

        ist = io.BytesIO(json.dumps(self.model_data).encode('utf-8'))
        rv = self.test_client.put(ARTIFACT_URL_WITH_ID.format(PROJECT_ID,
                                                              ITERATION_ID,
                                                              str(ObjectId())),
                                  input_stream=ist,
                                  headers=self.headers)
        self.assertTrue(rv._status_code == 404)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_get_artifacts(self, *args, **kwargs):
        id_to_get = str(self.data.mongo_id)
        rv = self.test_client.get(ARTIFACT_URL.format(PROJECT_ID,
                                                      ITERATION_ID),
                                  headers=self.headers)
        result_collection = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(rv._status_code == 200,
                        "got status code " + str(rv.status_code))
        self.assertTrue(len(result_collection) == 1)
        self.assertTrue(result_collection[0].get('id') == id_to_get)
        get_record_dic = self.data.wrap()
        clean_nonserializable_attributes(get_record_dic)
        for key in get_record_dic:
            self.assertEqual(get_record_dic[key], result_collection[0].
                             get(key), "assertion failed for key {} ".
                             format(key))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_get_artifacts_item(self, *args, **kwargs):
        id_to_get = str(self.data.mongo_id)
        rv = self.test_client.get(ARTIFACT_URL_WITH_ID.format(PROJECT_ID,
                                                              ITERATION_ID,
                                                              id_to_get),
                                  headers=self.headers)
        result = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(rv._status_code == 200)
        self.assertTrue(id_to_get == result['id'])
        get_record_dic = self.data.wrap()
        clean_nonserializable_attributes(get_record_dic)
        for key in get_record_dic:
            self.assertEqual(get_record_dic[key], result.get(key),
                             "assertion failed for key {} ".format(key))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_get_artifacts_item_not_found(self, *args, **kwargs):
        rv = self.test_client.get(ARTIFACT_URL_WITH_ID.format(PROJECT_ID,
                                                              ITERATION_ID,
                                                              str(ObjectId())),
                                  headers=self.headers)
        self.assertTrue(rv._status_code == 404)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(system_user_auth_response(), 200))
    def test_delete_artifacts_item(self, *args, **kwargs):
        id_to_delete = str(self.data.mongo_id)
        rv = self.test_client.delete(ARTIFACT_URL_WITH_ID.format(PROJECT_ID,
                                                                 ITERATION_ID,
                                                                 id_to_delete),
                                     headers=self.headers)
        self.assertTrue(rv._status_code == 204)
        deleted_record = Artifacts.query.get(id_to_delete)
        self.assertIsNone(deleted_record)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(system_user_auth_response(), 200))
    def test_delete_artifacts_item_notfound(self, *args, **kwargs):

        rv = self.test_client.delete(ARTIFACT_URL_WITH_ID.format(PROJECT_ID,
                                                                 ITERATION_ID,
                                                                 str
                                                                 (ObjectId())),
                                     headers=self.headers)
        self.assertTrue(rv._status_code == 404)

    @patch('mongomock.write_concern.WriteConcern.__init__',
           return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(no_auth_response(), 401))
    def test_get_artifacts_not_authorized(self, *args, **kwargs):
        rv = self.test_client.get(ARTIFACT_URL.format(SOME_OTHER_PROJECT_ID,
                                                      ITERATION_ID
                                                      ), headers=self.headers)
        self.assertTrue(rv._status_code == 401)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(invalid_auth_response(), 200))
    def test_get_artifacts_master_token(self, *args, **kwargs):
        rv = self.test_client.get(
            ARTIFACT_URL.format(PROJECT_ID, ITERATION_ID),
            headers=self.headers)
        self.assertTrue(rv._status_code == 403)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(no_auth_response(), 401))
    def test_get_artifacts_no_authorization(self, *args, **kwargs):
        rv = self.test_client.get(
            ARTIFACT_URL.format(PROJECT_ID, ITERATION_ID),
            headers=[('Content-Type', 'application/json')])
        self.assertTrue(rv._status_code == 401)

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
