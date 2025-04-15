# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class RolesEmployeeStructure(Document):
	def validate(self):
		self.validate_duplicate_roles()

	def validate_duplicate_roles(self):
		"""Validate that there are no duplicate roles for the same employee in the project"""
		if not self.parent or not self.parenttype or not self.employee or not self.role_type:
			return

		# Get the project document
		project = frappe.get_doc(self.parenttype, self.parent)
		
		# Check for duplicate roles in current project's table
		if project.get("table_sdso"):
			# Count how many times this employee-role combination exists
			count = 0
			for role in project.table_sdso:
				if role.employee == self.employee and role.role_type == self.role_type:
					count += 1
					if count > 1:  # If we find more than one occurrence
						frappe.throw(
							_("Employee {0} already has the role '{1}' in this project. Duplicate roles are not allowed.").format(
								self.employee, self.role_type
							)
						)
