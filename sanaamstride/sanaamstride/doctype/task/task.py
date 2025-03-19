import frappe
from frappe.model.document import Document
from frappe import _

class Task(Document):
    def validate(self):
        if self.project:
            is_parent = frappe.get_value("Project", self.project, "is_parent")
            if is_parent:
                frappe.throw(
                    _("Selected Project '{0}' is marked as a Parent Project.").format(self.project)
                )

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

