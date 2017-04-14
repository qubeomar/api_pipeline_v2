from qube.src.api import persist_db


class Artifacts(persist_db.Document):
    # Primary ID
    id = persist_db.StringField(required=False)

    # Artifacts  model data
    type = persist_db.StringField(required=False)
    contentType = persist_db.StringField(required=False)
    title = persist_db.StringField(required=False)
    url = persist_db.StringField(required=False)
    projectId = persist_db.StringField(required=False)
    iterationId = persist_db.StringField(required=False)

    # Default tracking data
    createdBy = persist_db.StringField(required=False)
    modifiedBy = persist_db.StringField(required=False)
    orgId = persist_db.StringField(required=True)
    tenantId = persist_db.StringField(required=True)
    createdDate = persist_db.StringField(required=False)
    modifiedDate = persist_db.StringField(required=True)
