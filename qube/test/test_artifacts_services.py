#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock
from mongomock import ObjectId

ITERATION_ID = "891011"

PROJECT_ID = "123456"
SOME_OTHER_PROJECT_ID = "456789"

with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['ARTIFACTS_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['ARTIFACTS_MONGOALCHEMY_SERVER'] = ''
    os.environ['ARTIFACTS_MONGOALCHEMY_PORT'] = ''
    os.environ['ARTIFACTS_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.artifacts import Artifacts
    from qube.src.services.artifactsservice import ArtifactsService
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, ArtifactsServiceError


class TestArtifactsService(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.artifactsService = ArtifactsService(context)
        self.artifacts_api_model = self.createTestModelData()
        self.artifacts_data = \
            self.setupDatabaseRecords(PROJECT_ID, ITERATION_ID,
                                      self.artifacts_api_model)
        self.artifacts_someoneelses = \
            self.setupDatabaseRecords(SOME_OTHER_PROJECT_ID, ITERATION_ID,
                                      self.artifacts_api_model)
        self.artifacts_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.artifacts_someoneelses.save()
        self.artifacts_api_model_for_update \
            = self.createTestModelDataUpdate()
        self.test_data_collection = [self.artifacts_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.artifacts_data.remove()

    def createTestModelData(self):
        return {
            'type': 'test123123124',
            'contentType': 'html',
            'title': 'test',
            'url': 'test'
        }

    def createTestModelDataUpdate(self):
        return {'type': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, project_id, iteration_id,
                             artifacts_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            artifacts_data = Artifacts()
            for key in artifacts_api_model:
                artifacts_data.__setattr__(key, artifacts_api_model[key])

            artifacts_data.projectId = project_id
            artifacts_data.iterationId = iteration_id
            artifacts_data.tenantId = "23432523452345"
            artifacts_data.orgId = "987656789765670"
            artifacts_data.createdBy = "1009009009988"
            artifacts_data.modifiedBy = "1009009009988"
            artifacts_data.createDate = str(int(time.time()))
            artifacts_data.modifiedDate = str(int(time.time()))
            artifacts_data.save()
            return artifacts_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_artifacts(self, *args, **kwargs):
        project_id = '123456'
        iteration_id = '78910'
        result = self.artifactsService.save(self.artifacts_api_model,
                                            project_id, iteration_id)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['title'] == self.artifacts_api_model['title'])
        self.assertEqual(result['projectId'], project_id)
        self.assertEqual(result['iterationId'], iteration_id)
        self.assertTrue(result['url'] == self.artifacts_api_model['url'])
        self.assertTrue(result['contentType'] == self.artifacts_api_model[
            'contentType'])
        self.assertTrue(result['type'] == self.artifacts_api_model[
            'type'])
        Artifacts.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_artifacts(self, *args, **kwargs):
        self.artifacts_api_model['title'] = 'modified for put'
        id_to_find = str(self.artifacts_data.mongo_id)
        result = self.artifactsService.update(
            self.artifacts_api_model, PROJECT_ID, ITERATION_ID, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['title'] == self.artifacts_api_model['title'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_artifacts_type(self, *args, **kwargs):
        self.artifacts_api_model_for_update['type'] =\
            'modified for put'
        id_to_find = str(self.artifacts_data.mongo_id)
        result = self.artifactsService.update(
            self.artifacts_api_model_for_update, PROJECT_ID, ITERATION_ID,
            id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(
            result['type'] ==
            self.artifacts_api_model_for_update['type'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_artifacts_item(self, *args, **kwargs):
        id_to_find = str(self.artifacts_data.mongo_id)
        result = self.artifactsService.find_by_id(PROJECT_ID, ITERATION_ID,
                                                  id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_artifacts_item_invalid(self, *args, **kwargs):
        id_to_find = ObjectId()
        with self.assertRaises(ArtifactsServiceError):
            self.artifactsService.find_by_id(PROJECT_ID, ITERATION_ID,
                                             id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_artifacts_list(self, *args, **kwargs):
        result_collection = self.artifactsService.get_all(PROJECT_ID,
                                                          ITERATION_ID)
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.artifacts_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_artifact_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.artifacts_data.mongo_id)
        with self.assertRaises(ArtifactsServiceError) as ex:
            self.artifactsService.\
                delete(PROJECT_ID, ITERATION_ID, id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_artifact_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.artifacts_data.mongo_id)
        self.artifactsService.auth_context.is_system_user = True
        self.artifactsService.delete(PROJECT_ID, ITERATION_ID, id_to_delete)
        with self.assertRaises(ArtifactsServiceError) as ex:
            self.artifactsService.find_by_id(PROJECT_ID, ITERATION_ID,
                                             id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.artifactsService.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_artifact_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.artifacts_someoneelses.mongo_id)
        with self.assertRaises(ArtifactsServiceError):
            self.artifactsService.delete(SOME_OTHER_PROJECT_ID,
                                         ITERATION_ID,
                                         id_to_delete)
