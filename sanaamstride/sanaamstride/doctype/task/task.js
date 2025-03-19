frappe.ui.form.on("Task", {
    refresh: function (frm) {
        // Set filter for Project field to exclude parent projects
        frm.set_query("project", function () {
            return {
                filters: {
                    is_parent: 0
                }
            };
        });

        // Set filter for Parent Task to only allow tasks within the same project
        frm.set_query("parent_task", function () {
            return {
                filters: {
                    project: frm.doc.project
                }
            };
        });

        // Button to calculate task hours from sub-tasks
        frm.add_custom_button(__('Calculate Hours'), function () {
            frappe.call({
                method: "sanaamstride.sanaamstride.doctype.task.task.calculate_hours",
                args: { task: frm.doc.name },
                callback: function (r) {
                    frm.refresh_field("expected_hours_count");
                    frm.refresh_field("actual_hours_count");
                    frappe.msgprint("Task Hours Updated!");
                }
            });
        });
    }
});
