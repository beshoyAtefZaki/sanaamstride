import frappe
from frappe.model.document import Document
from frappe import _

class Task(Document):
    def validate(self):
        # Validation for assigning employees based on sprint flag
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

        # Validate that any child task in the child table is only of type "Task" or "Error"
        self.validate_child_task_types()

    def validate_child_task_types(self):
        """
        Ensure that if the Task has a child table (named "child_tasks"),
        each child row's "type" field is either "Task" or "Error".
        """
        if self.get("child_tasks"):
            for child in self.child_tasks:
                if child.type not in ["Task", "Error"]:
                    frappe.throw(_("Invalid Child Task Type: Only 'Task' or 'Error' are allowed. Found: {0}").format(child.type))


@frappe.whitelist()
def create_sprint_task_from_project(current_project, task_name, is_sprint=1, description=None):
    """
    Create a new Task with the sprint flag set to true.
    In this version, since the Task doctype no longer includes fields for project linkage,
    we only set task_name, is_sprint, and description.
    """
    new_task = frappe.new_doc("Task")
    new_task.task_name = task_name
    new_task.is_sprint = int(is_sprint)  # Force is_sprint to true (1)
    new_task.description = description
    new_task.insert()  # Save the new Task document
    return new_task.name
