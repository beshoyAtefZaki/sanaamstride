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
        """Fetch project name and sprint from Task doctype and update the child table."""
        for row in self.get("employee_tasks_sheet"):
            if row.task:
                task_doc = frappe.get_doc("Task", row.task)
                row.project = task_doc.project  # Assign project from task
                row.sprint = task_doc.sprint    # Assign sprint from task

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
            project_sheet.posted_date = self.date  # Assign date
            project_sheet.sprint = row.sprint           # Assign sprint
            
            project_sheet.actual_hours = row.actual_hours  # Assign actual hours
            project_sheet.insert(ignore_permissions=True)
            
            # Update task actual hours and status
            task_doc = frappe.get_doc("Task", row.task)
            task_doc.actual_hours_count += row.actual_hours
            
            # Update task status if it's different from the current status
            if row.status and task_doc.status != row.status:
                task_doc.status = row.status
                
            task_doc.save(ignore_permissions=True)
            #update project actual hours
            frappe.db.commit()
        frappe.msgprint(_("Project Sheet Entries created successfully."), alert=True)

@frappe.whitelist()
def update_task_status(task, status):
    """Update the status of a task when changed in the Time Sheet."""
    try:
        if not task or not status:
            frappe.throw(_("Task and status are required."))
            
        # Get the task document
        task_doc = frappe.get_doc("Task", task)
        
        # Update the status
        task_doc.status = status
        
        # Save with ignore permissions
        task_doc.flags.ignore_permissions = True
        task_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return True
    except Exception as e:
        frappe.logger().error(f"Error updating task status: {str(e)}")
        frappe.throw(_("Error updating task status: {0}").format(str(e)))
