frappe.ui.form.on('Task', {
    refresh: function(frm) {
        // Initialize the form
        frm.set_value('type', 'sprint');
        
        // Add debug log
        console.log("Task form refreshed");

        if (frm.doc.type === "sprint") {
            // Add a button to manually calculate total hours
            frm.add_custom_button(__('Calculate Total Hours'), function() {
                calculate_sprint_hours(frm);
            });

            // Show total hours in the form
            if (frm.doc.total_actual_hours) {
                frm.add_custom_info('Total Actual Hours: ' + frm.doc.total_actual_hours);
            }
        }
    },
    
    validate: function(frm) {
        if (frm.doc.is_sprint && frm.doc.project) {
            frm.doc.__copy_employees = true;
        }
    },
    
    before_save: function(frm) {
        // Check if this is a sprint task and has a project
        if (frm.doc.type === "sprint" && frm.doc.project) {
            console.log("Sprint task detected, will copy employees after save");
            frm.doc.__copy_employees = true;
        }
    },
    
    after_save: function(frm) {
        if (frm.doc.__copy_employees) {
            console.log("Copying employees from project:", frm.doc.project);
            
            frappe.call({
                method: 'sanaamstride.sanaamstride.doctype.project.project.copy_employees_to_sprint',
                args: {
                    'parent_project': frm.doc.project,
                    'sprint_task': frm.doc.name
                },
                freeze: true,
                freeze_message: __("Copying employees..."),
                callback: function(r) {
                    if (r.message) {
                        frm.reload_doc();
                        frappe.show_alert({
                            message: __('Employees copied successfully'),
                            indicator: 'green'
                        });
                    }
                }
            });
        }

        // Automatically calculate hours when a sprint task is saved
        if (frm.doc.type === "sprint") {
            calculate_sprint_hours(frm);
        }
    },

    is_sprint: function(frm) {
        if (frm.doc.is_sprint && !frm.doc.project) {
            frappe.msgprint(__('Please select a project first'));
            frm.set_value('is_sprint', 0);
            return;
        }
    },
    
    project: function(frm) {
        // Clear the tasked_assigned_employee table when project changes
        if (frm.doc.project) {
            frm.set_value('tasked_assigned_employee', []);
        }
    }
});

function calculate_sprint_hours(frm) {
    frappe.call({
        method: 'sanaamstride.sanaamstride.doctype.project.project.get_sprint_total_hours',
        args: {
            'sprint_task': frm.doc.name
        },
        freeze: true,
        freeze_message: __("Calculating total hours..."),
        callback: function(r) {
            if (r.message !== undefined) {
                frm.reload_doc();
                frappe.show_alert({
                    message: __('Total actual hours updated: {0}', [r.message]),
                    indicator: 'green'
                });
            }
        }
    });
}