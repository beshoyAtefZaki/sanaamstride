import frappe

def get_sprint_list(*args, **kwargs):
    response = []
    
    # Fetch all Sprint tasks (Tasks that are sprints)
    sprints = frappe.get_all(
        "Task", 
        filters={"is_sprint": 1},
        fields=["name", "name1", "status"]
    )
    
    for sprint in sprints:
        sprint_title = sprint.get("name1", sprint.get("name"))
        
        # Fetch sprint tasks for this sprint.
        sprint_tasks = frappe.get_all(
            "Task",
            filters={
                "sprint": sprint["name"],
                "type": ["in", ["Task", "Error"]]
            },
            fields=["name", "name1", "status", "employee"]
        )
        
        response.append({
            "sprint": sprint["name"],
            "sprint_title": sprint_title,
            "sprint_status": sprint["status"],
            "tasks": sprint_tasks
        })
    
    return response
