import frappe
from frappe import _

@frappe.whitelist()
def get_projectList(*args, **kwargs):
    """
    Returns all parent projects, their child projects,
    and for each child project its sprints and tasks.
    """
    response = []

    # 1) Fetch parent projects
    parents = frappe.get_all(
        "Project",
        filters={"is_parent": 1},
        fields=["name", "project_name", "status"]
    )

    for p in parents:
        # 2) Fetch child projects
        children = frappe.get_all(
            "Project",
            filters={"parent_project": p.name},
            fields=["name", "project_name", "status"]
        )

        enriched_children = []
        for c in children:
            # 3a) Sprints under this child project
            sprints = frappe.get_all(
                "Task",
                filters={"project": c.name, "is_sprint": 1},
                fields=["name", "name1 as sprint_name", "status"]
            )
            # 3b) Tasks under this child project
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
