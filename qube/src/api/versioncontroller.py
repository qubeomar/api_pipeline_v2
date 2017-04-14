#!/usr/bin/python
"""
Add docstring here
"""
from flask_restful_swagger_2 import Resource, swagger

from qube.src.api.swagger_models.artifacts import VersionModel
from qube.src.api.swagger_models.response_messages import \
    ErrorModel, response_msgs
from qube.src.commons.log import Log as LOG
from qube.src.commons.qube_config import QubeConfig

EMPTY = ''


class ArtifactsItemVersionController(Resource):
    def __init__(self, *args, **kwargs):
        super(ArtifactsItemVersionController, self).__init__(*args, **kwargs)
        self.config = QubeConfig.get_config()

    @swagger.doc(
        {
            'tags': ['Artifacts'],
            'description': 'Artifacts Version operation',
            'responses': response_msgs
        }
    )
    def get(self):
        """gets an artifacts item that omar has changed
        """
        try:
            LOG.debug("Get version ")
            return VersionModel(**{'version': self.config.get_version()}), 200
        except Exception as ex:
            LOG.error(ex)
            return ErrorModel(**{'message': ex}), 500
