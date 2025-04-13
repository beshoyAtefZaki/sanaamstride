
import frappe 

def execute(*args ,**kwargs):
    roles =["Manager"  , "Employee"  , "Supervisor"]
    for role_name in roles :
        if not frappe.db.exists("Role" , role_name) :
            role = frappe.new_doc("Role")
            role.role_name = role_name
            role.insert(ignore_permissions=True ,ignore_if_duplicate=True) 
    frappe.db.commit()
    print ("Roles Created Successfully")
