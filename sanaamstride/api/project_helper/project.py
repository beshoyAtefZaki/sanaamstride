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
       
        response.append({
            "parent" : project.name,
            "parent_name" : project.project_name,
            "parent_status" : project.status,
            "child" : child_projects,
           
        })
    return response
