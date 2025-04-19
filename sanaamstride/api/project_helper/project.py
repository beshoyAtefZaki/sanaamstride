
# import frappe 


# #child project list with sprints and tasks .

# @frappe.whitelist(allow_guest=True)
# def get_all():
#     """
#     API endpoint to get all projects with their child projects, sprints and tasks
#     URL: /api/method/sanaamstride.api.project.get_all
#     """
#     response = []
#     parent_projects = frappe.get_all("Project", filters = {"is_parent" : 1} ,
#                                                 fields = ["name" ,
#                                                         "project_name" , 
#                                                         "status" ]
#                                     )
#     for project in parent_projects :
#         child_projects = frappe.get_all("Project", 
#                                         filters = {"parent_project" : project.name} ,
#                                          fields = ["name" ,
#                                                         "project_name" , 
#                                                         "status" ]
#                                     )
        
#         # Get sprints and tasks for each child project
#         child_projects_with_details = []
#         for child in child_projects:
#             # Get sprints for this child project
#             sprints = frappe.get_all("Task",
#                                    filters={"project": child.name, "is_sprint": 1},
#                                    fields=["name", "name1 as sprint_name", "status"])
            
#             # Get tasks for this child project
#             tasks = frappe.get_all("Task",
#                                  filters={"project": child.name, "is_sprint": 0},
#                                  fields=["name", "name1 as task_name", "status"])
            
#             child_projects_with_details.append({
#                 "name": child.name,
#                 "project_name": child.project_name,
#                 "status": child.status,
#                 "sprints": sprints,
#                 "tasks": tasks
#             })
        
#         response.append({
#             "name": project.name,
#             "project_name": project.project_name,
#             "status": project.status,
#             "child_projects": child_projects_with_details
#         })
#     return response

import frappe
from frappe import _

@frappe.whitelist()
def get_projectList(project_name=None, **kwargs):
    """
    Returns all parent projects (is_parent = 1), filtered by project_name if provided,
    each with its child projects, and for each child project its sprints and tasks.
    """
    response = []

    parent_filters = {"is_parent": 1}
    if project_name:
        parent_filters["project_name"] = ["like", f"%{project_name}%"]

    parents = frappe.get_all(
        "Project",
        filters=parent_filters,
        fields=["name", "project_name", "status"]
    )

    for p in parents:
        children = frappe.get_all(
            "Project",
            filters={"parent_project": p.name},
            fields=["name", "project_name", "status"]
        )

        enriched_children = []
        for c in children:
            sprints = frappe.get_all(
                "Task",
                filters={"project": c.name, "is_sprint": 1},
                fields=["name", "name1 as sprint_name", "status"]
            )
            tasks = frappe.get_all(
                "Task",
                filters={"project": c.name, "is_sprint": 0},
                fields=["name", "name1 as task_name", "status"]
            )
            enriched_children.append({
                "name": c.name,
                "project_name": c.project_name,
                "status": c.status,
                "sprints": sprints,
                "tasks": tasks
            })

        response.append({
            "name": p.name,
            "project_name": p.project_name,
            "status": p.status,
            "child_projects": enriched_children
        })

    return response


@frappe.whitelist()
def create_project_service(project_name, is_parent=1, parent_project=None, status="Waiting", description="", **kwargs):
    
    is_parent = int(is_parent)
    if not project_name:
        frappe.throw(_("`project_name` is required."))

    # Validate status
    valid_statuses = ["Waiting", "on progress", "Hold", "Completed", "Cancels"]
    if status not in valid_statuses:
        frappe.throw(_(f"Status cannot be \"{status}\". It should be one of {', '.join(valid_statuses)}"))

    if is_parent not in (0, 1):
        frappe.throw(_("'is_parent' must be 0 or 1."))

    if is_parent == 0:
        if not parent_project:
            frappe.throw(_("`parent_project` is required for a child project."))
        parent_doc = frappe.get_doc("Project", parent_project)
        if not parent_doc.is_parent:
            frappe.throw(_(f"Project {parent_project} is not marked as a parent."))

    proj = frappe.new_doc("Project")
    proj.project_name = project_name
    proj.is_parent = is_parent
    proj.status = status
    proj.description = description or ""
    if is_parent == 0:
        proj.parent_project = parent_project

    proj.insert(ignore_permissions=True)
    return proj.name

