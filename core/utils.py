# core/utils.py


def is_privileged_user(user):
    """Checks if a user is a Superuser or has the MANAGEMENT role."""
    return user.is_authenticated and (user.is_superuser or user.role == 'MANAGEMENT')


def is_pm_user(user):
    """
    Checks if user is a Project Manager.
    PM = MANAGER role + Project Management department.
    Superusers are also considered PM-capable.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return (
        getattr(user, 'role', None) == 'MANAGER' and
        getattr(user, 'department', None) == 'Project Management'
    )


def is_sm_user(user):
    """
    Checks if user is Senior Management.
    SM = MANAGEMENT role + Senior Management department.
    Superusers are also considered SM-capable.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return (
        getattr(user, 'role', None) == 'MANAGEMENT' and
        getattr(user, 'department', None) == 'Senior Management'
    )


def log_change(model_type, object_id, action, changed_by, changes):
    """
    Creates a ChangeLog entry for audit trail.

    Args:
        model_type (str): 'PROJECT', 'TASK', or 'EVENT'
        object_id (int): Primary key of the changed object
        action (str): 'CREATE', 'UPDATE', or 'DELETE'
        changed_by (User): The user who made the change
        changes (dict): Dictionary of {field: old_value} for updates
    """
    try:
        from .models import ChangeLog
        ChangeLog.objects.create(
            model_type=model_type,
            object_id=object_id,
            action=action,
            changed_by=changed_by,
            changes=changes or {}
        )
    except Exception:
        # Never let audit logging break the main operation
        pass