# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class Employee(Document):
	def validate(self):
		self.create_user()
		self.validate_roles()
		self.validate_user_roles()

	def validate_user(self):
		if not self.user :
			return True
		else :
			if not frappe.db.exists("User", {"email": self.email}) :
				return True
			else :
				False 
	def create_user(self) :
		if self.validate_user() :
			naming_list  = str(self.employee_name).split(" ")
			user = frappe.new_doc("User")
			user.email = self.email
			user.first_name = naming_list[0]
			if len(naming_list) > 1:
				user.last_name = naming_list[1]
			user.enabled = 1
			user.save()
			self.user = user.name
		else :
			return "user already exists"
	
	def validate_roles(self):
		"""Validate that there are no duplicate roles assigned to the employee"""
		if self.get("roles"):
			seen_roles = set()
			for role in self.roles:
				if role.role in seen_roles:
					frappe.throw(f"Duplicate role '{role.role}' found for employee {self.employee_name}. An employee cannot have the same role multiple times.")
				seen_roles.add(role.role)

	def validate_user_roles(self):
		"""Validate that the user has all the same roles as the employee"""
		if not self.user:
			return

		# Get all roles assigned to the employee
		employee_roles = set()
		if self.get("roles"):
			employee_roles = {role.role for role in self.roles}

		# Get all roles assigned to the user
		user_roles = set()
		user = frappe.get_doc("User", self.user)
		if user.get("roles"):
			user_roles = {role.role for role in user.roles}

		# Check if user is missing any roles that the employee has
		missing_roles = employee_roles - user_roles
		if missing_roles:
			frappe.throw(
				_("User {0} is missing the following roles that the employee has: {1}. Please assign these roles to the user.").format(
					self.user, ", ".join(missing_roles)
				)
			)
	
	def has_role(self, role) :
		return role in [role.role for role in self.roles]
	
	def copy_roles_to_child_project(self, child_project):
		# Step 1: Retrieve roles from the parent project
		parent_roles = frappe.get_all("Role", filters={"parent": self.name}, fields=["employee", "role_type"])

		# Step 2: Create roles in the child project
		for role in parent_roles:
			new_role = frappe.new_doc("Role")
			new_role.employee = role.employee
			new_role.role_type = role.role_type
			new_role.parent = child_project.name  # Set the parent to the new child project
			new_role.insert()  # Save the new role in the child project
	
	def create_child_project(self):
		# Logic to create the child project
		child_project = frappe.new_doc("Project")
		child_project.name = "New Child Project"
		child_project.insert()

		# Copy roles from the parent project to the child project
		self.copy_roles_to_child_project(child_project)
	
