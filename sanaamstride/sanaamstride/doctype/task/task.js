frappe.ui.form.on("Task", {
    refresh(frm) {
        // Toggle fields based on is_sprint value
        frm.toggle_enable("tasked_assigned_employee", frm.doc.is_sprint ? 1 : 0);
        frm.toggle_enable("employee", frm.doc.is_sprint ? 0 : 1);
        frm.toggle_enable("linked_task", frm.doc.is_sprint ? 0 : 1);

        // If there's a child table "child_tasks" with a link field "task"
        // Filter that link field to only show tasks with type "Task" or "Error"
        if (frm.fields_dict.child_tasks) {
            frm.fields_dict.child_tasks.grid.get_field("task").get_query = function() {
                return {
                    filters: {
                        type: ["in", ["Task", "Error"]]
                    }
                };
            };
        }
    },

    is_sprint(frm) {
        frm.trigger("refresh");
    },

    end_date(frm) {
        if (frm.doc.start_date && frm.doc.end_date) {
            if (frm.doc.end_date < frm.doc.start_date) {
                frappe.msgprint(__("End Date cannot be before Start Date."));
                frappe.validated = false;
            }
        }
    },

    onload(frm) {
        // Set query for the 'project' field (if used) to only show projects where is_parent is false (or other filter)
        frm.set_query("project", function() {
            return {
                filters: {
                    is_parent: 0
                }
            };
        });
    }
});
