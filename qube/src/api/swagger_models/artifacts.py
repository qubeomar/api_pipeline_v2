from flask_restful_swagger_2 import Schema


class VersionModel(Schema):
    type = 'object'
    properties = {
        'version': {
            'type': 'string',
        }
    }


class ArtifactsModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'string',
        },
        'type': {
            'type': 'string',
        },
        'contentType': {
            'type': 'string',
        },
        'title': {
            'type': 'string'
        },
        'url': {
            'type': 'string'
        },
        'isResource': {
            'type': 'boolean',
            'default': 'false'
        },
        'projectId': {
            'type': 'string',
        },
        'iterationId': {
            'type': 'string',
        },
        'tenantId': {
            'type': 'string'
        },
        'orgId': {
            'type': 'string'
        },
        'createdBy': {
            'type': 'string'
        },
        'createdDate': {
            'type': 'string'
        },
        'modifiedBy': {
            'type': 'string'
        },
        'modifiedDate': {
            'type': 'string'
        }
    }
    required = ['title']


class ArtifactListModel(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'string',
        },
        'type': {
            'type': 'string',
        },
        'contentType': {
            'type': 'string',
        },
        'title': {
            'type': 'string'
        },
        'isResource': {
            'type': 'boolean',
            'default': 'false'
        },
        'projectId': {
            'type': 'string',
        },
        'iterationId': {
            'type': 'string',
        },
        'tenantId': {
            'type': 'string'
        },
        'orgId': {
            'type': 'string'
        },
        'createdBy': {
            'type': 'string'
        },
        'createdDate': {
            'type': 'string'
        },
        'modifiedBy': {
            'type': 'string'
        },
        'modifiedDate': {
            'type': 'string'
        }
    }
    required = ['title']


class ArtifactsModelPost(Schema):
    type = 'object'
    properties = {
        'type': {
            'type': 'string',
        },
        'contentType': {
            'type': 'string',
        },
        'title': {
            'type': 'string'
        },
        'url': {
            'type': 'string'
        },
        'isResource': {
            'type': 'boolean',
            'default': 'false'
        }
    }
    required = ['title']


class ArtifactsModelPut(Schema):
    type = 'object'
    properties = {
        'type': {
            'type': 'string',
        },
        'contentType': {
            'type': 'string',
        },
        'title': {
            'type': 'string'
        },
        'url': {
            'type': 'string'
        },
        'isResource': {
            'type': 'boolean',
            'default': 'false'
        }
    }


class ArtifactsModelPostResponse(Schema):
    type = 'object'
    properties = {
        'id': {
            'type': 'string'
        }
    }


class ArtifactsErrorModel(Schema):
    type = 'object'
    properties = {
        'error_code': {
            'type': 'string'
        },
        'error_message': {
            'type': 'string'
        }
    }
    required = ['title']
