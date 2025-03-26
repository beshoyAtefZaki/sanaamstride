import frappe
from frappe.model.document import Document
from frappe import _

class TimeSheet(Document):
    def validate(self):
        """Ensure project is pulled from selected task in child table before submission."""
        self.set_project_from_task()

    def on_submit(self):
        """On submission, create project sheet entries based on time sheet details."""
        self.create_project_sheet_entries()

    def set_project_from_task(self):
        """Fetch project name from Task doctype and update the child table."""
        for row in self.get("employee_tasks_sheet"):
            if row.task:
                task_doc = frappe.get_doc("Task", row.task)
                row.project = task_doc.project  # Assign project from task

    def create_project_sheet_entries(self):
        """Automatically creates Project Sheet Entry records for each task in the time sheet."""
        if not self.get("employee_tasks_sheet"):
            frappe.msgprint(_("No tasks found in the Time Sheet."), alert=True)
            return
        
        for row in self.get("employee_tasks_sheet"):
            if not row.task:
                continue  # Skip if no task is assigned

            project_sheet = frappe.new_doc("Project Sheet Entry")
            project_sheet.timesheet = self.name        # Link to the Time Sheet
            project_sheet.employee = self.employee    # Assign employee
            project_sheet.task = row.task             # Assign task
            project_sheet.project = row.project       # Assign project

            project_sheet.insert(ignore_permissions=True)

        frappe.msgprint(_("Project Sheet Entries created successfully."), alert=True)
