import frappe 

from sanaamstride.api.project_helper.project import get_all

@frappe.whitelist()
def get_all_projects(*args , **kwargs) :
    return get_all(*args , **kwargs)