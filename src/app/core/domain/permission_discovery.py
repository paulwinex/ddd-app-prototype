import importlib
import inspect
from pathlib import Path
from typing import TypeVar

from loguru import logger

from app.core.domain.permissions_base import PermissionsBase
import app

T = TypeVar("T", bound=PermissionsBase)


def discover_permission_enums() -> list[type[PermissionsBase]]:
    """
    List of permission enum classes
    """
    permission_classes: list[type[PermissionsBase]] = []
    
    # Get root path from the package
    base_path = Path(app.__file__).parent
    for perm_file in base_path.glob("*/domain/permissions.py"):
        rel_path = perm_file.relative_to(base_path.parent)
        module_name = str(rel_path.with_suffix("")).replace("/", ".")

        try:
            module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    inspect.isclass(attr)
                    and issubclass(attr, PermissionsBase)
                    and attr is not PermissionsBase
                    and attr not in permission_classes
                ):
                    permission_classes.append(attr)
                    logger.info(f"Discovered permission enum: {module_name}.{attr_name}")

        except Exception as e:
            logger.warning(f"Failed to import {module_name}: {e}")

    return permission_classes


def get_all_permissions() -> list[PermissionsBase]:
    """
    Get all permission instances from all discovered permission enums.

    Returns:
        List of all permission instances
    """
    permission_classes = discover_permission_enums()
    all_permissions: list[PermissionsBase] = []

    for perm_class in permission_classes:
        all_permissions.extend(perm_class.get_all_permissions())

    return all_permissions
