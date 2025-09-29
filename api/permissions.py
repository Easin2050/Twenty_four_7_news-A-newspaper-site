from rest_framework import permissions

class FullDjangoModelPermissions(permissions.DjangoModelPermissions):
    
    def __init__(self):
        self.perms_map['GET']= ['%(app_label)s.add_%(model_name)s']
        self.perms_map['GET']= ['%(app_label)s.change_%(model_name)s']
        self.perms_map['GET']= ['%(app_label)s.delete_%(model_name)s']
        self.perms_map['GET']= ['%(app_label)s.view_%(model_name)s']

class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsReviewOwnerOrReadOnly(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  
            return True
        return obj.user == request.user