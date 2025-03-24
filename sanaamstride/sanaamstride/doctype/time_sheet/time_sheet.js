frappe.ui.form.on("Time Sheet", {
    refresh(frm) {
        // Set a custom query for the "task" link field in the child table "employee_tasks_sheet_child"
        frm.set_query("task", "employee_tasks_sheet", function(doc, cdt, cdn) {
            return {
                filters: {
                    type: ["in", ["Task", "Error"]],
                    employee: frm.doc.employee
                }
            };
        });
    }
});

frappe.ui.form.on("Employee Tasks Sheet", {
    task: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.task) {
            frappe.db.get_doc("Task", row.task).then(task_doc => {
                // Set the project field in the child table to the project from the selected Task.
                frappe.model.set_value(cdt, cdn, "project", task_doc.project);
            });
        } else {
            // Optionally, clear the project field if no task is selected.
            frappe.model.set_value(cdt, cdn, "project", "");
        }
    }
});



