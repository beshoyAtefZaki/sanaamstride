import frappe
from sanaamstride.api.project_helper.project import get_projectList, create_project_service

@frappe.whitelist()
def get_all(project_name=None, **kwargs):
    return get_projectList(project_name=project_name, **kwargs)

@frappe.whitelist()
def create_project(project_name, is_parent=1, parent_project=None, status="Waiting", description=None, **kwargs):

    return create_project_service(
        project_name=project_name,
        is_parent=is_parent,
        parent_project=parent_project,
        status=status,
        description=description or "",
        **kwargs
    )
