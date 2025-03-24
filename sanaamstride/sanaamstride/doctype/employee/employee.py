# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Employee(Document):
	def validate(self):
		self.create_user()

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
			user.last_name = naming_list[1]
			user.enabled = 1
			user.save()
			self.user = user.name
		else :
			return "user already exists"
	def has_role(self, role) :
		return role in [role.role for role in self.roles]
	
