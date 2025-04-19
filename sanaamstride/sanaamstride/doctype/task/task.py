import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import today
from sanaamstride.sanaamstride.doctype.project.project import calculate_total_actual_hours ,calculate_total_actual_hours_virtual
class Task(Document):
    def validate(self):
        self.update_status()
        self.set_date()
        self.validate_sprint()
        # Validation for assigning employees based on sprint flag
        
        
        self.validate_child_task_types()
    def before_save(self):
        """Validate Expected Hours Count for sprint tasks before saving"""
       
            
        # If this is a task (not a sprint) and it has a sprint assigned
        
        # If this is a sprint task and has a project, copy employees from the project
        if self.is_sprint and self.project:
            self.copy_employees_from_project()
    def on_change(self) :
        pass
        # self.calculate_parent_sprint_hours_()
        # self.calculate_parent_sprint_hours_()

    @property
    def total_hours(self) :
        if not self.is_sprint and self.sprint:
            if self.actual_hours_count :
                return int(self.actual_hours_count )
            return 0
        else :
            return calculate_total_actual_hours_virtual(self.name) 
    def update_status(self):
        if self.status not in ["ToDo"]:
            """
            check if there ara sprint  and sprint status = Todo set the status to In Progress
            check linked project  and update status if still waitting  
            check parent project status and update 
            """
            if self.sprint:
                sprint = frappe.get_doc("Task", self.sprint)
                if sprint.status == "ToDo":
                    sprint.status = "On Progress"
                    sprint.save()
            if self.project:
                project = frappe.get_doc("Project", self.project)
                if project.status == "Waiting":
                    project.status = "on progress"
                    project.save()

                if project.is_parent == False:
                    parent_project = frappe.get_doc("Project", project.parent_project)
                    if parent_project.status == "Waiting":
                        parent_project.status = "on progress"
                        parent_project.save()
    def set_date(self) :
        #set date if not set 
        if self.status != "ToDo"    and not self.start_date: 
            self.start_date = today()

    def validate_sprint(self) :
        if not self.is_sprint:
            if self.get("tasked_assigned_employee") and len(self.tasked_assigned_employee) > 0:
                frappe.throw(
                    _("You cannot assign employees in the child table unless this is a Sprint (is_sprint = true).")
                )
        if self.is_sprint and self.employee:
            frappe.throw(_("You cannot set an Employee if this Task is marked as a Sprint."))
        if self.is_sprint == 1 and not self.expected_hours_count:
            frappe.throw(
                _("Expected Hours Count is required for Sprint tasks. Please enter the expected hours.")
            )
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

    def calculate_parent_sprint_hours_(self):
        if not self.is_sprint and self.sprint:
            # Get the old document if it exists
            old_doc = self.get_doc_before_save()
            # Check if actual_hours_count has changed
            if old_doc and old_doc.actual_hours_count != self.actual_hours_count:
                calculate_total_actual_hours(self.sprint)
    def copy_employees_from_project(self):
        """Copy employees from the project's Role table to the sprint's Tasked Assigned Employee table"""
        try:
            # Get the project document
            project_doc = frappe.get_doc("Project", self.project)
            
            # Check if the project has a parent project
            if project_doc.parent_project:
                # Get the parent project document
                parent_project_doc = frappe.get_doc("Project", project_doc.parent_project)
                
                # Check if the parent project has roles
                if parent_project_doc.get("table_sdso"):
                    # Clear existing assigned employees
                    self.set("tasked_assigned_employee", [])
                    
                    # Copy employees from parent project
                    for role in parent_project_doc.table_sdso:
                        if role.employee:
                            self.append("tasked_assigned_employee", {
                                "employee": role.employee,
                                "parentfield": "tasked_assigned_employee",
                                "parenttype": "Task"
                            })
                    
                    frappe.msgprint(_("Employees copied from parent project to sprint task."))
            else:
                # If no parent project, use the project's own roles
                if project_doc.get("table_sdso"):
                    # Clear existing assigned employees
                    self.set("tasked_assigned_employee", [])
                    
                    # Copy employees from project
                    for role in project_doc.table_sdso:
                        if role.employee:
                            self.append("tasked_assigned_employee", {
                                "employee": role.employee,
                                "parentfield": "tasked_assigned_employee",
                                "parenttype": "Task"
                            })
                    
                    frappe.msgprint(_("Employees copied from project to sprint task."))
        except Exception as e:
            frappe.logger().error(f"Error copying employees to sprint task: {str(e)}")
            frappe.msgprint(_("Error copying employees to sprint task: {0}").format(str(e)))

   

   

   
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
def create_sprint_task_from_project(current_project, task_name, is_sprint=1, description=None ,sprint = None, expected_hours_count=None):
    """
    Create a new Task with the sprint flag set to true.
    """
    # if is_sprint and not expected_hours_count:
    #     frappe.throw(_("Expected Hours Count is required for Sprint tasks. Please enter the expected hours."))
  
    new_task = frappe.new_doc("Task")
    new_task.name1 = task_name
    new_task.is_sprint = 1 if not sprint else 0 # Force is_sprint to true (1)
    new_task.description = description
    new_task.project = current_project
    new_task.expected_hours_count = expected_hours_count
    if sprint :
        new_task.sprint = sprint
    new_task.insert()  # Save the new Task document
    return new_task.name

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_employee(doctype, txt, searchfield, start, page_len, filters) :
   
    #we need project as filter 
    parent_name = filters.get("project")
    Child  = frappe.qb.DocType("Roles  Employee Structure")
    Employee = frappe.qb.DocType("Employee")
    sql_query = (
		frappe.qb.from_(Child).inner_join(Employee).on(Child.employee == Employee.name).
		select(Child.employee , Employee.employee_name , Employee.phone , Employee.email).
        where((Child.parent == f"{parent_name} ") & (Child.role_type == "Employee")  )
	)
     
    return sql_query.run()

@frappe.whitelist()
def copy_employees_from_project(task_name):
    """Copy employees from the project's Role table to the sprint's Tasked Assigned Employee table"""
    try:
        # Get the task document
        task_doc = frappe.get_doc("Task", task_name)
        
        # Check if this is a sprint task
        if not task_doc.is_sprint:
            frappe.throw(_("This task is not a sprint task."))
        
        # Check if the task has a project
        if not task_doc.project:
            frappe.throw(_("This sprint task does not have a project assigned."))
        
        # Call the copy_employees_from_project method
        task_doc.copy_employees_from_project()
        
        # Save the task
        task_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        return True
    except Exception as e:
        frappe.logger().error(f"Error copying employees to sprint task: {str(e)}")
        frappe.throw(_("Error copying employees to sprint task: {0}").format(str(e)))
