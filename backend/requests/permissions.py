from rest_framework import permissions

class IsFacultyOwner(permissions.BasePermission):
    """
    Allows Faculty to view or edit their own requests.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'FACULTY' or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'faculty_profile') and obj.faculty == request.user.faculty_profile

class IsHODDepartment(permissions.BasePermission):
    """
    Allows HOD to view and act on requests from their own department.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'HOD' or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'hod_profile') and obj.department == request.user.hod_profile.department

class IsDeanComputing(permissions.BasePermission):
    """
    Allows Dean of Computing to view/approve computing cluster requests in PENDING_DEAN state.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'DEAN_COMPUTING' or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        computing_depts = ['CSE', 'CSE(CS)', 'AIDS', 'IT', 'CSBS']
        return obj.department.department_code.upper() in computing_depts

class IsManagementAO(permissions.BasePermission):
    """
    Allows Management/AO to view, approve, and manage all requests.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'MANAGEMENT' or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return True

class IsPrincipal(permissions.BasePermission):
    """
    Allows Principal to view and give final approval on requests.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'PRINCIPAL' or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return True
