#!/usr/bin/python
"""
Add docstring here
"""
from flask import request
from flask_restful_swagger_2 import Resource, swagger
from mongoalchemy.exceptions import ExtraValueException

from qube.src.api.decorators import login_required
from qube.src.api.swagger_models.artifacts import ArtifactListModel,\
    ArtifactsModel # noqa: ignore=I100
from qube.src.api.swagger_models.artifacts import ArtifactsModelPost # noqa: ignore=I100
from qube.src.api.swagger_models.artifacts import ArtifactsModelPostResponse # noqa: ignore=I100
from qube.src.api.swagger_models.artifacts import ArtifactsModelPut # noqa: ignore=I100

from qube.src.api.swagger_models.parameters import (
    body_post_ex, body_put_ex, header_ex, path_ex, path_ex_iteration,
    path_ex_project)
from qube.src.api.swagger_models.response_messages import (
    del_response_msgs, ErrorModel, get_response_msgs, get_all_response_msgs,
    post_response_msgs, put_response_msgs)
from qube.src.commons.error import ArtifactsServiceError
from qube.src.commons.log import Log as LOG
from qube.src.commons.utils import clean_nonserializable_attributes
from qube.src.services.artifactsservice import ArtifactsService

EMPTY = ''
get_details_params = [header_ex, path_ex_project, path_ex_iteration, path_ex]
put_params = [header_ex, path_ex_project, path_ex_iteration, path_ex,
              body_put_ex]
delete_params = [header_ex, path_ex_project, path_ex_iteration, path_ex]
get_params = [header_ex, path_ex_project, path_ex_iteration]
post_params = [header_ex, body_post_ex, path_ex_project, path_ex_iteration]


class ArtifactsItemController(Resource):
    @swagger.doc(
        {
            'tags': ['Artifacts'],
            'description': 'Artifacts get operation',
            'parameters': get_details_params,
            'responses': get_response_msgs
        }
    )
    @login_required
    def get(self, authcontext, project_id, iteration_id, entity_id):
        """gets an artifacts item
        """
        try:
            LOG.debug("Get details by id %s %s %s", project_id, iteration_id,
                      entity_id)
            data = ArtifactsService(authcontext['context'])\
                .find_by_id(project_id, iteration_id, entity_id)
            clean_nonserializable_attributes(data)
        except ArtifactsServiceError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), e.errors
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': e.args[0]}), 400
        return ArtifactsModel(**data), 200

    @swagger.doc(
        {
            'tags': ['Artifacts'],
            'description': 'Artifacts put operation',
            'parameters': put_params,
            'responses': put_response_msgs
        }
    )
    @login_required
    def put(self, authcontext, project_id, iteration_id, entity_id):
        """
        updates an artifacts item
        """
        try:
            model = ArtifactsModelPut(**request.get_json())
            context = authcontext['context']
            ArtifactsService(context).update(model, project_id, iteration_id,
                                             entity_id)
            return EMPTY, 204
        except ArtifactsServiceError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), e.errors
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': e.args[0]}), 400
        except Exception as ex:
            LOG.error(ex)
            return ErrorModel(**{'error_code': '500',
                                 'error_message': ex.args[0]}), 500

    @swagger.doc(
        {
            'tags': ['Artifacts'],
            'description': 'Artifacts delete operation',
            'parameters': delete_params,
            'responses': del_response_msgs
        }
    )
    @login_required
    def delete(self, authcontext, project_id, iteration_id, entity_id):
        """
        Delete artifacts item
        """
        try:
            ArtifactsService(authcontext['context']).delete(project_id,
                                                            iteration_id,
                                                            entity_id)
            return EMPTY, 204
        except ArtifactsServiceError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), e.errors
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': e.args[0]}), 400
        except Exception as ex:
            LOG.error(ex)
            return ErrorModel(**{'error_code': '500',
                                 'error_message': ex.args[0]}), 500


class ArtifactsController(Resource):
    @swagger.doc(
        {
            'tags': ['Artifacts'],
            'description': 'Artifacts get all operation',
            'parameters': get_params,
            'responses': get_all_response_msgs
        }
    )
    @login_required
    def get(self, authcontext, project_id, iteration_id):
        """
        gets all artifacts items
        """
        LOG.debug("Serving  Get all request")
        list = ArtifactsService(authcontext['context']).get_all(project_id,
                                                                iteration_id)
        artifacts_list = []
        for data in list:
            clean_nonserializable_attributes(data)
            if 'url' in data:
                del data['url']
            artifacts_list_model = ArtifactListModel(**data)
            artifacts_list.append(artifacts_list_model)

        # normalize the name for 'id'
        return artifacts_list, 200

    @swagger.doc(
        {
            'tags': ['Artifacts'],
            'description': 'Artifacts create operation',
            'parameters': post_params,
            'responses': post_response_msgs
        }
    )
    @login_required
    def post(self, authcontext, project_id, iteration_id):
        """
        Adds a artifacts item.
        """
        try:
            model = ArtifactsModelPost(**request.get_json())
            result = ArtifactsService(authcontext['context'])\
                .save(model, project_id, iteration_id)

            response = ArtifactsModelPostResponse()
            for key in response.properties:
                response[key] = result[key]

            return (response, 201,
                    {'Location': request.path + '/' + str(response['id'])})
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), 400
        except ExtraValueException as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': "{} is not valid input".
                              format(e.args[0])}), 400
        except Exception as ex:
            LOG.error(ex)
            return ErrorModel(**{'error_code': '500',
                                 'error_message': ex.args[0]}), 500
