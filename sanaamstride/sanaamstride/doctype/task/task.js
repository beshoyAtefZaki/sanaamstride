frappe.ui.form.on("Task", {


    create_sprint_task_dialog(frm) {
		let d = new frappe.ui.Dialog({
			title: 'Enter Sprint Task Details',
			fields: [
				{
					label: 'Task Name',
					fieldname: 'task_name',
					fieldtype: 'Data',
					reqd: 1
				},
				{
					label: 'Is Sprint',
					fieldname: 'is_sprint',
					fieldtype: 'Check',
					default: 0,
					read_only: 1
				},
				{
					label: 'Description',
					fieldname: 'description',
					fieldtype: 'Small Text',
					reqd: 1
				},
			],
			size: 'small',
			primary_action_label: 'Submit',
			primary_action(values) {
				frappe.call({
					method: 'sanaamstride.sanaamstride.doctype.task.task.create_sprint_task_from_project',
					args: {
						current_project: frm.doc.project,
						task_name: values.task_name,
						is_sprint: values.is_sprint,  // will always be 1
						description: values.description ,
                        sprint : frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frappe.show_alert({
								message: __('Sprint Task created successfully: {0}', [r.message]),
								indicator: 'green'
							});
							d.hide();
							frappe.set_route('Form', 'Task', r.message);
						}
					}
				});
			}
		});
		d.show();
	},
    add_create_task(frm) {
        frm.add_custom_button(__("Create Task"), function() {
            // Open the dialog to create a sprint task
            frm.events.create_sprint_task_dialog(frm);
        });
    },
    setup(frm){

        frm.set_query("sprint" ,function() {
            return {
                filters: {
                    is_sprint: 1 ,
                    project: frm.doc.project ,
                    name: ['!=', frm.doc.name]
                }
            };
        });

    },
    
    refresh(frm) {
        // frm.toggle_enable("tasked_assigned_employee", frm.doc.is_sprint ? 1 : 0);
        frm.toggle_enable("employee", frm.doc.is_sprint ? 0 : 1);
        frm.toggle_enable("linked_task", frm.doc.is_sprint ? 0 : 1);
        frm.events.setup(frm)
        if (frm.doc.is_sprint) {
            frm.events.add_create_task(frm);
        }
       
    },
    type:(frm) => {
       if (frm.doc.type == "Sprint") {
           frm.set_value("is_sprint", 1);
           frm.events.add_create_task(frm);
       }
       else {
           frm.set_value("is_sprint", 0);
       }
       frm.refresh_field("is_sprint");
    },
    is_sprint(frm) {
        frm.trigger("refresh");
    },
    project(frm) {
        frm.trigger("setup");
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
