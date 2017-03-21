
class AuthContext:
    def __init__(self, tenant_id, tenant_name, org_id, org_name,
                 user_id, user_name, is_system_user):
        self.tenant_id = tenant_id
        self.org_id = org_id
        self.user_id = user_id
        self.is_system_user = is_system_user
        self.tenant_name = tenant_name
        self.org_name = org_name
        self.user_name = user_name
