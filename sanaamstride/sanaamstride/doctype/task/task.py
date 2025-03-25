import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today
class Task(Document):

    def update_status(self) :
        if self.status not in ["ToDo"] :
            """
            check if there ara sprint  and sprint status = Todo set the status to In Progress
            check linked project  and update status if still waitting  
            check parent project status and update 
            """
            if self.sprint :
                sprint = frappe.get_doc("Task", self.sprint)
                if sprint.status == "ToDo" :
                    sprint.status = "On Progress"
                    sprint.save()
            if self.project :
                project = frappe.get_doc("Project", self.project)
                if project.status == "Waiting" :
                    project.status = "on progress"
                    project.save()

                if project.is_parent ==False :
                    parent_project = frappe.get_doc("Project", project.parent_project)
                    if parent_project.status == "Waiting" :
                        parent_project.status = "on progress"
                        parent_project.save()
    def validate(self):
        self.update_status()
        if self.status != "ToDo"    and not self.start_date: 
            self.start_date = today()
         
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
def create_sprint_task_from_project(current_project, task_name, is_sprint=1, description=None ,sprint = None):
    """
    Create a new Task with the sprint flag set to true.
    In this version, since the Task doctype no longer includes fields for project linkage,
    we only set task_name, is_sprint, and description.
    """
    new_task = frappe.new_doc("Task")
    new_task.name1 = task_name
    new_task.is_sprint = int(is_sprint)  # Force is_sprint to true (1)
    new_task.description = description
    new_task.project = current_project
    if sprint :
        new_task.sprint = sprint
    new_task.insert()  # Save the new Task document
    return new_task.name
