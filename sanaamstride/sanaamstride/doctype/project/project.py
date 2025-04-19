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


@frappe.whitelist()
def copy_employees_to_sprint(parent_project, sprint_task):
    """Copy employees from parent project to sprint task"""
    try:
        # Debug logging
        frappe.logger().debug(f"Starting copy_employees_to_sprint: project={parent_project}, task={sprint_task}")
        
        # Get parent project
        parent_project_doc = frappe.get_doc("Project", parent_project)
        if not parent_project_doc.table_sdso:
            frappe.msgprint(_("No employees found in the parent project."))
            return False
            
        # Get sprint task
        sprint_task_doc = frappe.get_doc("Task", sprint_task)
        
        # Ensure this is a sprint task
        if sprint_task_doc.type != "sprint":
            frappe.throw(_("This task is not marked as a sprint task."))
        
        # Clear existing assigned employees
        sprint_task_doc.set("tasked_assigned_employee", [])
        
        # Copy employees from project
        for role in parent_project_doc.table_sdso:
            if role.employee:
                frappe.logger().debug(f"Copying employee {role.employee} to task")
                sprint_task_doc.append("tasked_assigned_employee", {
                    "employee": role.employee,
                    "parentfield": "tasked_assigned_employee",
                    "parenttype": "Task"
                })
        
        # Save with ignore permissions
        sprint_task_doc.flags.ignore_permissions = True
        sprint_task_doc.flags.ignore_links = True
        sprint_task_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        frappe.logger().debug("Successfully copied employees to sprint task")
        return True
        
    except Exception as e:
        frappe.logger().error(f"Error copying employees to sprint: {str(e)}")
        frappe.throw(_("Error copying employees to sprint task: {0}").format(str(e)))

@frappe.whitelist()
def calculate_total_actual_hours(sprint_name = None):
	if not sprint_name :
		frappe.throw(_("Sprint name is required."))
	"""Calculate total actual hours for completed tasks in a sprint and update sprint's actual hours count."""
	try:
		# First verify that the sprint exists
		if not frappe.db.exists("Task", sprint_name):
			frappe.throw(_("Sprint '{0}' not found").format(sprint_name))
			
		# Fetch all tasks related to the sprint
		tasks = frappe.get_all("Task", filters={"sprint": sprint_name, "status": "Completed"}, fields=["name", "actual_hours_count"])
		
		# Sum the actual hours of completed tasks
		total_hours = sum(task.get("actual_hours_count", 0) for task in tasks)
		
		# Create a breakdown of actual hours for each task
		task_hours = {task['name']: task.get("actual_hours_count", 0) for task in tasks}
		
		# Update the sprint's actual_hours_count
		sprint_doc = frappe.get_doc("Task", sprint_name)
		sprint_doc.actual_hours_count = total_hours
		sprint_doc.save(ignore_permissions=True)
		
		frappe.db.commit()
		
		frappe.msgprint(_("Sprint total hours updated to: {0}").format(total_hours))
		return total_hours, task_hours
	except Exception as e:
		frappe.logger().error(f"Error calculating total actual hours for sprint {sprint_name}: {str(e)}")
		frappe.throw(_("Error calculating total actual hours: {0}").format(str(e)))




def calculate_total_actual_hours_virtual(sprint_name = None):
	"""
	convert to calculate actual hours from Project Sheet Entry
	
	"""
	if not sprint_name :
		frappe.throw(_("Sprint name is required."))
	"""Calculate total actual hours for completed tasks in a sprint and update sprint's actual hours count."""
	try:
		# First verify that the sprint exists
		if not frappe.db.exists("Task", sprint_name):
			frappe.throw(_("Sprint '{0}' not found").format(sprint_name))
			
		# Fetch all tasks related to the sprint
		tasks = frappe.get_all("Task", filters={"sprint": sprint_name, "status": "Completed"}, fields=["name", "actual_hours_count"])
		
		# Sum the actual hours of completed tasks
		total_hours = sum(task.get("actual_hours_count", 0) for task in tasks)
		
		# Create a breakdown of actual hours for each task
		task_hours = {task['name']: task.get("actual_hours_count", 0) for task in tasks}
		
		# Update the sprint's actual_hours_count
		# sprint_doc = frappe.get_doc("Task", sprint_name)
		# sprint_doc.actual_hours_count = total_hours
		# sprint_doc.save(ignore_permissions=True)
		
		# frappe.db.commit()
		
		# frappe.msgprint(_("Sprint total hours updated to: {0}").format(total_hours))
		return total_hours
	except Exception as e:
		frappe.logger().error(f"Error calculating total actual hours for sprint {sprint_name}: {str(e)}")
		frappe.throw(_("Error calculating total actual hours: {0}").format(str(e)))
