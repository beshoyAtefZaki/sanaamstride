# Copyright (c) 2025, beshoy atef and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Task(Document):
    def validate(self):
        self.validate_project()
        self.validate_parent_task()
        self.calculate_hours()

    def validate_project(self):
        if self.project:
            project = frappe.get_doc("Project", self.project)
            if project.is_parent:
                frappe.throw("You cannot assign tasks to a parent project. Please select a valid project.")

    def validate_parent_task(self):
        if self.parent_task:
            parent = frappe.get_doc("Task", self.parent_task)
            if parent.is_sprint:
                frappe.throw("A sprint task cannot be a parent task.")

    def calculate_hours(self):
        if self.get("parent_task"):
            parent = frappe.get_doc("Task", self.parent_task)
            sub_tasks = frappe.get_all(
                "Task",
                filters={"parent_task": self.parent_task},
                fields=["expected_hours_count", "actual_hours_count"]
            )
            parent.expected_hours_count = sum(task["expected_hours_count"] for task in sub_tasks)
            parent.actual_hours_count = sum(task["actual_hours_count"] for task in sub_tasks)
            parent.save()

@frappe.whitelist()
def get_project_tasks(project):
    """Get all tasks in a project"""
    return frappe.get_all("Task", filters={"project": project}, fields=["name", "status", "expected_hours_count"])
