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
                frappe.model.set_value(cdt, cdn, "sprint", task_doc.sprint || "");
                frappe.model.set_value(cdt, cdn, "status", task_doc.status || "");
            });
        } else {
            frappe.model.set_value(cdt, cdn, "project", "");
            frappe.model.set_value(cdt, cdn, "sprint", "");
            frappe.model.set_value(cdt, cdn, "status", "");
        }
    },
    
    status: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.task && row.status) {
            // Update the task status
            frappe.call({
                method: 'sanaamstride.sanaamstride.doctype.time_sheet.time_sheet.update_task_status',
                args: {
                    'task': row.task,
                    'status': row.status
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.show_alert({
                            message: __('Task status updated to {0}', [row.status]),
                            indicator: 'green'
                        });
                    }
                }
            });
        }
    }
});
