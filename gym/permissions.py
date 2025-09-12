from rest_framework import permissions
class IsAdministrator(permissions.BasePermission):
    def has_permission(self,request,view):
        return(
            request.user and
            request.user.is_authenticated and
            request.user.is_administrator()
        )

class IsCoach(permissions.BasePermission):
    def has_permission(self,request,view):
        return(
            request.user and
            request.user.is_authenticated and
            request.user.is_coach()
        )
        
class IsClient(permissions.BasePermission):
    def has_permission(self,request,view):
        return(
            request.user and
            request.user.is_authenticated and
            request.user.is_client()
        )
class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request,view,obj):
        if request.user.is_administrator():
            return True
        return obj == request.user