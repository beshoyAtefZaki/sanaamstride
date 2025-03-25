from __future__ import unicode_literals
import frappe
from .project import get_tasks

__version__ = '1.0.0'

@frappe.whitelist()
def get_tasks_api(*args, **kwargs):
    return get_tasks(*args, **kwargs) 