import frappe
from frappe.model.document import Document
from frappe import _

class TimeSheet(Document):
    def on_submit(self):
        self.create_project_sheet_entry()

    def create_project_sheet_entry(self):
        """
        Automatically creates a Project Sheet Entry based on the Time Sheet details.
        Adjust field names based on your actual doctype definitions.
        """
        project_sheet = frappe.new_doc("Project Sheet Entry")
        project_sheet.timesheet = self.name       # Link to this Time Sheet
        project_sheet.employee = self.employee     # Copy the employee from the Time Sheet
        if hasattr(self, "project"):
            project_sheet.project = self.project    # Link to the project if available

        project_sheet.insert(ignore_permissions=True)
        frappe.msgprint(_("Project Sheet Entry {0} created successfully.").format(project_sheet.name))
