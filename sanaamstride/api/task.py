import frappe 

from sanaamstride.api.task_helper.task import get_sprint_list

@frappe.whitelist()
def get_all_sprint(*args , **kwargs) :
    return get_sprint_list(*args , **kwargs)