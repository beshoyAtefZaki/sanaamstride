// Copyright (c) 2025, beshoy atef and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project", {
	// Function to create a new sub-project (existing functionality)
	create_project_dialog(frm) {
		let d = new frappe.ui.Dialog({
			title: 'Enter details',
			fields: [
				{
					label: 'Project Name',
					fieldname: 'project_name',
					fieldtype: 'Data',
					reqd: 1
				},
				{
					label: 'Is Parent',
					fieldname: 'is_parent',
					fieldtype: 'Check',
					default: 0,
					read_only: 1
				},
				{
					label: 'Parent Project',
					fieldname: 'parent_project',
					fieldtype: 'Link',
					options: 'Project',
					read_only: 1,
					default: frm.doc.name,
					get_query: function() {
						return {
							filters: {
								is_parent: 1
							}
						};
					}
				},
				{
					label: 'Description',
					fieldname: 'description',
					fieldtype: 'Small Text',
					reqd: 1
				},
			],
			size: 'small', // small, large, extra-large 
			primary_action_label: 'Submit',
			primary_action(values) {
				frappe.call({
					method: 'sanaamstride.sanaamstride.doctype.project.project.create_sup_project',
					args: {
						current_project: frm.doc.name,
						project_name: values.project_name,
						parent_project: frm.doc.name,
						is_parent: 0,
						description: values.description
					},
					callback: function(r) {
						if (r.message) {
							frappe.show_alert({
								message: __(`Project created successfully ${r.message}`),
								indicator: 'green'
							});
							d.hide();
							frappe.set_route('Form', 'Project', r.message);
						}
					}
				});
			}
		});
		d.show();
	},

	// Function to create a new Sprint Task via dialog
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
					default: 1,
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
						current_project: frm.doc.name,
						task_name: values.task_name,
						project: frm.doc.name,
						is_sprint: values.is_sprint,  // will always be 1
						description: values.description ,
						expected_hours_count : 10
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

	apply_filter(frm) {
		frm.set_query("parent_project", function() {
			return {
				filters: {
					is_parent: 1
				}
			};
		});
	},

	refresh(frm) {
		// Show/hide buttons based on the is_parent value
		if (frm.doc.is_parent) {
			frm.add_custom_button(__("Create Project"), function() {
				frm.events.create_project_dialog(frm);
			}, __("Utilities"));
		}
		if (frm.doc.is_parent == false) {
			frm.add_custom_button(__("Create Task"), function() {
				frappe.new_doc("Task", {
					project: frm.doc.name
				});
			});
			frm.add_custom_button(__("Create Sprint"), function() {
				// Open the dialog to create a sprint task
				frm.events.create_sprint_task_dialog(frm);
			});
		}

		// Add Calculate Hours button
		frm.add_custom_button(__("Calculate Hours"), function() {
			calculate_project_hours(frm);
		});
	},

	status(frm) {
		if (frm.doc.status === "Completed") {
			calculate_project_hours(frm);
		}
	},

	onload(frm) {
		// Set initial visibility of the parent_project field
		frm.toggle_display('parent_project', !frm.doc.is_parent);
	}
});

// Function to calculate project hours from associated Tasks and Sprints
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
