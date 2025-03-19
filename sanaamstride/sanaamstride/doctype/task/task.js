frappe.ui.form.on("Task", {
    refresh(frm) {
        frm.toggle_enable("tasked_assigned_employee", frm.doc.is_sprint ? 1 : 0);
        frm.toggle_enable("employee", frm.doc.is_sprint ? 0 : 1);
        frm.toggle_enable("linked_task", frm.doc.is_sprint ? 0 : 1);
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

    onload: function(frm) {
        // Set the query for the 'project' field to only show projects where is_parent is true
        frm.set_query("project", function() {
            return {
                filters: {
                    is_parent: 0
                }
            };
        });
    }
});
