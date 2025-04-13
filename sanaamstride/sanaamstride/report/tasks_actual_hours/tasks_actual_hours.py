# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe




def get_columns():
	columns = [
		{
			"label": "Task",
			"fieldname": "task",
			"fieldtype": "Link",
			"options": "Task",
			"width": 200,
		},
		{
			"label": "Employee",
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 200,
		},
		{
			"label": "Project",
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 200,
		},
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			
			"width": 200,
		}
	]
	return columns

def get_data(filters=None):
	# You can add your logic here to fetch data based on filters
	data = []
	# if filters:
	# 	# Example: Fetch data based on filters
	# 	data = frappe.get_all("Task", filters=filters, fields=["name", "employee", "project"])
	# else:
	# 	data = frappe.get_all("Task", fields=["name", "employee", "project"])  "tabProject Sheet Entry"
	doctype = frappe.qb.DocType("Project Sheet Entry")
	Project = frappe.qb.DocType("Project")
	# sql_query = """ 
	# 	SELECT task , employee , project   from `tabProject Sheet Entry`  
	# 	"""
	sql_query = (
		frappe.qb.from_(doctype).inner_join(Project).on(doctype.project == Project.name).
		select(doctype.task, doctype.employee, doctype.project , Project.status).where(doctype.project == "PRO-0004")
	
	)
	return sql_query.run()
def execute(filters=None):
	columns, data = get_columns(), get_data()
	return columns, data
