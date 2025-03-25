import frappe
from frappe import _

@frappe.whitelist()  # This decorator whitelists the method for API access
def get_tasks(*args, **kwargs):
    try:
        response = []
        
        # Get all sprints (Tasks with type="Sprint")
        sprints = frappe.get_all("Task", 
                                fields=["name", "name1 as sprint_name"],
                                filters={
                                    "type": "Sprint",
                                    "status": ["!=", "Canceled"]
                                }
                                )
        
        if not sprints:
            return {"data": []}
        
        for sprint in sprints:
            # Get tasks for each sprint
            tasks = frappe.get_all("Task",
                                  filters={
                                      "sprint": sprint.name,
                                      "type": "Task",
                                      "status": ["!=", "Canceled"]
                                  },
                                  fields=["name", "name1 as subject", "status", "employee as assigned_to", "task_descerption as description"]
                                  )
            
            if tasks:  # Only add sprints that have tasks
                response.append({
                    "sprint": sprint.sprint_name,
                    "tasks": tasks
                })
        
        return {"data": response}
    
    except Exception as e:
        frappe.log_error(
            title="Error in get_tasks API",
            message=str(e)
        )
        return {"data": [], "error": str(e)}
