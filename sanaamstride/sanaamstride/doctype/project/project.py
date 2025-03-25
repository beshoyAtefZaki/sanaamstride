# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Project(Document):
	@property
	def total_sup_projects(self):
		return (frappe.db.count("Project", filters={"parent_project": self.name}))
	def set_dates(self) :
		if self.status not in ["Waiting"] :
			if not self.expected_start_date :
				self.expected_start_date = frappe.utils.today()
			if not self.start_date :
				self.start_date = frappe.utils.today()
	def validate(self):
		self.set_dates()
		self.validate_parent_project()
		

	def validate_parent_project(self):
		if self.parent_project:
			if frappe.get_value("Project", self.parent_project, "is_parent") == 0:
				frappe.throw("Parent Project must be a group")



@frappe.whitelist()
def create_sup_project( current_project ,project_name, parent_project , is_parent=0 , description=None):
	if current_project == parent_project:
		project = frappe.new_doc("Project")
		project.project_name = project_name
		project.parent_project = parent_project
		project.is_parent = is_parent
		project.description = description
		project.save()
		return project.name
	else:	
		frappe.throw("You can't create a sub project for another project")
	