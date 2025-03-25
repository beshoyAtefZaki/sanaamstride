import frappe 

from sanaamstride.api.project_helper.project import get_projectList

@frappe.whitelist()
def get_all(*args , **kwargs) :
    return get_projectList(*args , **kwargs)