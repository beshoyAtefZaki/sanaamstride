import frappe 



def get_projectList(*args , **kwargs) :
    response = []
    parent_projects = frappe.get_all("Project", filters = {"is_parent" : 1} ,
                                                fields = ["name" ,
                                                        "project_name" , 
                                                        "status" ]
                                    )
    for project in parent_projects :
        child_projects = frappe.get_all("Project", 
                                        filters = {"parent_project" : project.name} ,
                                         fields = ["name" ,
                                                        "project_name" , 
                                                        "status" ]
                                    )
        
        # Get sprints and tasks for each child project
        child_projects_with_details = []
        for child in child_projects:
            # Get sprints for this child project
            sprints = frappe.get_all("Task",
                                   filters={"project": child.name, "is_sprint": 1},
                                   fields=["name", "name1 as sprint_name", "status"])
            
            # Get tasks for this child project
            tasks = frappe.get_all("Task",
                                 filters={"project": child.name, "is_sprint": 0},
                                 fields=["name", "name1 as task_name", "status"])
            
            child_projects_with_details.append({
                "name": child.name,
                "project_name": child.project_name,
                "status": child.status,
                "sprints": sprints,
                "tasks": tasks
            })
        
        response.append({
            "name": project.name,
            "project_name": project.project_name,
            "status": project.status,
            "child_projects": child_projects_with_details
        })
    return response
