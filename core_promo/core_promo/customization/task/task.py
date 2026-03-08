import frappe


def validate(doc, event=None):
	if doc.subject and doc.custom_interaction_metrics and doc.project:
		create_task_work_log(doc)


def create_task_work_log(doc):
	twl_doc = frappe.new_doc("Task Work Log")
	twl_doc.project = doc.project
	twl_doc.task = doc.name
	if doc.custom_customer:
		twl_doc.customer = doc.custom_customer

	for row in doc.custom_interaction_metrics:
		twl_doc.append("task_detail", {"task__type": row.interaction_metrics, "count": row.count})

	twl_doc.save(ignore_permissions=True)
