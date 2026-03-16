from app.core.domain.permissions_base import PermissionsBase


class UserPermission(PermissionsBase, prefix="user"):
    CAN_EDIT_USER = "can_edit"
    CAN_ADD_USER = "can_add"
    CAN_DELETE_USER = "can_delete"
    CAN_VIEW_USER = "can_view"
    CAN_LIST_USERS = "can_list"


class GroupPermission(PermissionsBase, prefix="group"):
    CAN_EDIT_GROUP = "can_edit"
    CAN_ADD_GROUP = "can_add"
    CAN_DELETE_GROUP = "can_delete"
    CAN_VIEW_GROUP = "can_view"
    CAN_LIST_GROUPS = "can_list"
    CAN_MANAGE_GROUP_USERS = "can_manage_group_users"
    CAN_MANAGE_GROUP_PERMISSIONS = "can_manage_group_permissions"


class PermissionPermission(PermissionsBase, prefix="permission"):
    CAN_EDIT_PERMISSION = "can_edit"
    CAN_ADD_PERMISSION = "can_add"
    CAN_DELETE_PERMISSION = "can_delete"
    CAN_VIEW_PERMISSION = "can_view"
    CAN_LIST_PERMISSIONS = "can_list"

