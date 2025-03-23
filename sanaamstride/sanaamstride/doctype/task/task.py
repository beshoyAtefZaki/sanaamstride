import frappe
from frappe.model.document import Document
from frappe import _

class Task(Document):
    def validate(self):
        # Example validations; adjust as needed for your Task doctype
        if not self.is_sprint:
            if self.get("tasked_assigned_employee") and len(self.tasked_assigned_employee) > 0:
                frappe.throw(
                    _("You cannot assign employees in the child table unless this is a Sprint (is_sprint = true).")
                )

        if self.is_sprint and self.employee:
            frappe.throw(_("You cannot set an Employee if this Task is marked as a Sprint."))

        if getattr(self, "linked_task", None):
            if self.is_sprint:
                frappe.throw(
                    _("You cannot select a linked Task when 'is_sprint' is true.")
                )
            linked_doc = frappe.get_doc("Task", self.linked_task)
            if linked_doc.type != "Task":
                frappe.throw(
                    _("Linked Task must have type='Task'. You selected a different type.")
                )

@frappe.whitelist()
def create_sprint_task_from_project(current_project, task_name, is_sprint=1, description=None):
    """
    Create a new Task with the sprint flag set to true.
    In this version, since the Task doctype no longer contains a 'project' or a 'name1' field,
    we only set the task_name, is_sprint, and description.
    """
    new_task = frappe.new_doc("Task")
    new_task.task_name = task_name
    new_task.is_sprint = int(is_sprint)  # Force is_sprint to true (1)
    new_task.description = description
    new_task.insert()  # Save the new Task document
    return new_task.name
