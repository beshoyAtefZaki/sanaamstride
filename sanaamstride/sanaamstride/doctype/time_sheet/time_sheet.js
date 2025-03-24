frappe.ui.form.on("Time Sheet", {
    refresh(frm) {
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
                frappe.model.set_value(cdt, cdn, "project", task_doc.project || "");
            });
        } else {
            frappe.model.set_value(cdt, cdn, "project", "");
        }
    }
});
