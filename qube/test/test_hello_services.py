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


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['QUBE_SERVICE_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['QUBE_SERVICE_MONGOALCHEMY_SERVER'] = ''
    os.environ['QUBE_SERVICE_MONGOALCHEMY_PORT'] = ''
    os.environ['QUBE_SERVICE_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.hello import Hello
    from qube.src.services.helloservice import HelloService
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, HelloServiceError


class TestHelloService(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.helloService = HelloService(context)
        self.hello_api_model = self.createTestModelData()
        self.hello_data = self.setupDatabaseRecords(self.hello_api_model)
        self.hello_someoneelses = \
            self.setupDatabaseRecords(self.hello_api_model)
        self.hello_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.hello_someoneelses.save()
        self.hello_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.hello_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.hello_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, hello_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            hello_data = Hello(name='test_record')
            for key in hello_api_model:
                hello_data.__setattr__(key, hello_api_model[key])

            hello_data.description = 'my short description'
            hello_data.tenantId = "23432523452345"
            hello_data.orgId = "987656789765670"
            hello_data.createdBy = "1009009009988"
            hello_data.modifiedBy = "1009009009988"
            hello_data.createDate = str(int(time.time()))
            hello_data.modifiedDate = str(int(time.time()))
            hello_data.save()
            return hello_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_hello(self, *args, **kwargs):
        result = self.helloService.save(self.hello_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.hello_api_model['name'])
        Hello.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_hello(self, *args, **kwargs):
        self.hello_api_model['name'] = 'modified for put'
        id_to_find = str(self.hello_data.mongo_id)
        result = self.helloService.update(
            self.hello_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.hello_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_hello_description(self, *args, **kwargs):
        self.hello_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.hello_data.mongo_id)
        result = self.helloService.update(
            self.hello_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.hello_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_hello_item(self, *args, **kwargs):
        id_to_find = str(self.hello_data.mongo_id)
        result = self.helloService.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_hello_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(HelloServiceError):
            self.helloService.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_hello_list(self, *args, **kwargs):
        result_collection = self.helloService.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.hello_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.hello_data.mongo_id)
        with self.assertRaises(HelloServiceError) as ex:
            self.helloService.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.hello_data.mongo_id)
        self.helloService.auth_context.is_system_user = True
        self.helloService.delete(id_to_delete)
        with self.assertRaises(HelloServiceError) as ex:
            self.helloService.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.helloService.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.hello_someoneelses.mongo_id)
        with self.assertRaises(HelloServiceError):
            self.helloService.delete(id_to_delete)
