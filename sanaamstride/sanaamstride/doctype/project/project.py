# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


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
		self.validate_duplicate_roles()
		# Temporarily disabled for testing
		# self.validate_employee_user_roles()

	def validate_parent_project(self):
		if self.parent_project:
			if frappe.get_value("Project", self.parent_project, "is_parent") == 0:
				frappe.throw("Parent Project must be a group")

	def validate_duplicate_roles(self):
		"""Validate and remove duplicate roles for the same employee in the project"""
		if not self.get("table_sdso"):
			return

		# Create a dictionary to track employee-role combinations
		role_combinations = {}
		to_remove = []
		duplicate_messages = []
		
		# First pass: identify duplicates
		for idx, role in enumerate(self.table_sdso):
			if not role.employee or not role.role_type:
				continue
				
			key = f"{role.employee}-{role.role_type}"
			if key in role_combinations:
				to_remove.append(idx)
				duplicate_messages.append(
					_("Employee {0} already has the role '{1}' in this project.").format(
						role.employee, role.role_type
					)
				)
			else:
				role_combinations[key] = True

		# Remove duplicates in reverse order to maintain indices
		for idx in sorted(to_remove, reverse=True):
			self.table_sdso.pop(idx)
			
		if duplicate_messages:
			frappe.msgprint(
				_("The following duplicate roles were found and removed:<br>" + "<br>".join(duplicate_messages)),
				title=_("Duplicate Roles Removed"),
				alert=True
			)

	# Temporarily disabled for testing
	# def validate_employee_user_roles(self):
	# 	"""Validate that each employee's user has the required roles"""
	# 	if not self.get("table_sdso"):
	# 		return

	# 	for role in self.table_sdso:
	# 		if not role.employee or not role.role_type:
	# 			continue

	# 		# Get the employee document
	# 		employee = frappe.get_doc("Employee", role.employee)
	# 		if not employee.user:
	# 			frappe.throw(
	# 				_("Employee {0} does not have a user account. Please create a user account first.").format(
	# 					employee.employee_name
	# 				)
	# 			)

	# 		# Get the user document
	# 		user = frappe.get_doc("User", employee.user)
			
	# 		# Check if user has the required role
	# 		user_roles = {r.role for r in user.roles}
	# 		if role.role_type not in user_roles:
	# 			frappe.throw(
	# 				_("User {0} (associated with employee {1}) does not have the role '{2}'. Please assign this role to the user first.").format(
	# 					user.email, employee.employee_name, role.role_type
	# 				)
	# 			)


@frappe.whitelist()
def create_sup_project(current_project, project_name, parent_project, is_parent=0, description=None):
	if current_project == parent_project:
		# Create new project
		project = frappe.new_doc("Project")
		project.project_name = project_name
		project.parent_project = parent_project
		project.is_parent = is_parent
		project.description = description

		# Get parent project roles
		parent_project_doc = frappe.get_doc("Project", parent_project)
		if parent_project_doc.get("table_sdso"):
			# Copy roles from parent to child
			for role in parent_project_doc.table_sdso:
				project.append("table_sdso", {
					"employee": role.employee,
					"role_type": role.role_type
				})

		project.save()
		return project.name
	else:	
		frappe.throw("You can't create a sub project for another project")
	