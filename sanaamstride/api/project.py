<<<<<<< HEAD
import frappe 

from sanaamstride.api.project_helper.project import get_all

@frappe.whitelist()
def get_all_projects(*args , **kwargs) :
    return get_all(*args , **kwargs)
=======
import frappe 

from sanaamstride.api.project_helper.project import get_projectList

@frappe.whitelist()
def get_all(*args , **kwargs) :
    return get_projectList(*args , **kwargs)
>>>>>>> 175b140b904f41b7c7372ae02f6c23013a398be7
