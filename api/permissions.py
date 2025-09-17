from rest_framework import permissions

class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    
    def __init__(self):
        self.perms_map['GET']= ['%(app_label)s.add_%(model_name)s']
        self.perms_map['GET']= ['%(app_label)s.change_%(model_name)s']
        self.perms_map['GET']= ['%(app_label)s.delete_%(model_name)s']
        self.perms_map['GET']= ['%(app_label)s.view_%(model_name)s']
