# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Project(Document):
    @property
    def total_sup_projects(self):
        return frappe.db.count("Project", filters={"parent_project": self.name})

    def validate(self):
        if self.is_parent and self.parent_project:
            frappe.throw("A parent project cannot have a parent project assigned.")

        if self.expected_end_date and self.expected_start_date:
            if self.expected_end_date < self.expected_start_date:
                frappe.throw("Expected End Date cannot be before Expected Start Date.")

        self.calculate_project_hours()

        self.validate_parent_project()

    def calculate_project_hours(self):
        tasks = frappe.get_all(
            "Task",
            filters={"project": self.name},
            fields=["expected_hours_count", "actual_hours_count"]
        )

        self.total_project_hours = sum(
            task["actual_hours_count"] for task in tasks if task["actual_hours_count"]
        )
        self.total_tasks_expected_hours = sum(
            task["expected_hours_count"] for task in tasks if task["expected_hours_count"]
        )

    def validate_parent_project(self):
        if self.parent_project:
            parent_is_group = frappe.get_value("Project", self.parent_project, "is_parent")
            if parent_is_group == 0:
                frappe.throw("Parent Project must be a group (parent project).")


@frappe.whitelist()
def create_sup_project(current_project, project_name, parent_project, is_parent=0, description=None):
    """
    Creates a sub-project only if the current project is allowed to have sub-projects.

    :param current_project: The current project attempting to create a sub-project.
    :param project_name: The name of the new sub-project.
    :param parent_project: The parent project under which the sub-project will be created.
    :param is_parent: Whether the new sub-project should be a parent project itself.
    :param description: Additional description of the sub-project.
    :return: The name of the created sub-project.
    """

    if frappe.get_value("Project", parent_project, "is_parent") == 1:
        project = frappe.new_doc("Project")
        project.project_name = project_name
        project.parent_project = parent_project
        project.is_parent = is_parent
        project.description = description
        project.insert()
        return project.name
    else:
        frappe.throw("You can only create a sub-project under a valid parent project.")
