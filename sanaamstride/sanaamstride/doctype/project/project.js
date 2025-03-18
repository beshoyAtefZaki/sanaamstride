// Copyright (c) 2025, beshoy atef and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
	refresh(frm) {
        // Show/hide buttons based on is_parent value
        if (frm.doc.is_parent) {
            frm.add_custom_button(__("Create Task"), function() {
                frappe.new_doc("Task", {
                    project: frm.doc.name
                });
            });
            
            frm.add_custom_button(__("Create Sprint"), function() {
                frappe.new_doc("Sprint", {
                    project: frm.doc.name
                });
            });
        }
        
        // Add Calculate Hours button
        frm.add_custom_button(__("Calculate Hours"), function() {
            calculate_project_hours(frm);
        });
    },
    
    is_parent(frm) {
        // Show/hide parent_project field based on is_parent value
        frm.toggle_display('parent_project', !frm.doc.is_parent);
        // Refresh to update button visibility
        frm.refresh();
    },
    
    status(frm) {
        if (frm.doc.status === "Completed") {
            calculate_project_hours(frm);
        }
    },
    
    onload(frm) {
        // Set initial visibility of parent_project field
        frm.toggle_display('parent_project', !frm.doc.is_parent);
    }
});

function calculate_project_hours(frm) {
    // Get all tasks for this project
    frappe.db.get_list('Task', {
        filters: {
            project: frm.doc.name
        },
        fields: ['expected_hours']
    }).then(tasks => {
        let total_tasks_hours = 0;
        tasks.forEach(task => {
            total_tasks_hours += task.expected_hours || 0;
        });
        
        // Get all sprints for this project
        frappe.db.get_list('Sprint', {
            filters: {
                project: frm.doc.name
            },
            fields: ['expected_hours']
        }).then(sprints => {
            let total_sprints_hours = 0;
            sprints.forEach(sprint => {
                total_sprints_hours += sprint.expected_hours || 0;
            });
            
            // Calculate total project hours
            let total_project_hours = total_tasks_hours + total_sprints_hours;
            
            // Update the form
            frm.set_value('total_tasks_hours', total_tasks_hours);
            frm.set_value('total_sprints_hours', total_sprints_hours);
            frm.set_value('total_project_hours', total_project_hours);
        });
    });
}
