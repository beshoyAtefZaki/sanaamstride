// Copyright (c) 2025, beshoy atef and contributors
// For license information, please see license.txt

frappe.query_reports["Tasks Actual hours"] = {
	"filters": [
			{
				"fieldname": "project",
				"label": __("Project"),
				"options": "Project",
				"fieldtype": "Link",
			}
	]
};
