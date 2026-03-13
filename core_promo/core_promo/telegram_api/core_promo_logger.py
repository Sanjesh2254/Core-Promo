import json
import re

import frappe

ALLOWED_USERS = ["IFTTT", "Qamar Rizwani 🌛", "SAKTHIVEL MURUGAN S"]


@frappe.whitelist(allow_guest=True)
def telegram_webhook():
	try:
		raw_data = frappe.request.data

		if isinstance(raw_data, bytes):
			raw_data = raw_data.decode("utf-8")

		data = json.loads(raw_data)

		message = data.get("message", {})
		text = message.get("text", "")
		sender = message.get("from", {}).get("first_name")

		if not text:
			return {"status": "no text"}

		# ---- TASK MESSAGE ----
		if sender in ALLOWED_USERS and "TASK" in text.upper():
			chat_title = message.get("chat", {}).get("title")
			return create_task_from_message(text, chat_title)

		# ---- COUNT MESSAGE ----
		if re.search(r"\d+\s*c", text.lower()):
			return update_task_counts(text, sender)

		# ---- OTHER MESSAGES ----
		return handle_other_messages(text)

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Telegram Webhook Error")
		return {"status": "error"}


def create_task_from_message(text, chat_title):
	lines = text.split("\n")

	customer_name = None
	twitter_url = None
	customer = None
	comment_count = 0
	rt_count = 0

	for line in lines:
		line = line.strip()

		# Extract customer name
		if "TASK -" in line:
			customer_name = line.replace("TASK -", "").strip()

		# Comment count
		comment_match = re.search(r"(\d+)\s*(c|comments)", line.lower())
		if comment_match:
			comment_count = int(comment_match.group(1))

		# Retweet count
		rt_match = re.search(r"(\d+)\s*rt", line.lower())
		if rt_match:
			rt_count = int(rt_match.group(1))

		# Twitter link
		if "twitter.com" in line or "x.com" in line:
			twitter_url = line

	# -------------------------
	# Ensure Customer Exists
	# -------------------------
	if customer_name:
		customer = frappe.db.exists("Customer", {"customer_name": customer_name})

		if not customer:
			customer_doc = frappe.get_doc(
				{"doctype": "Customer", "customer_name": customer_name, "customer_type": "Company"}
			)
			customer_doc.insert(ignore_permissions=True)
			customer = customer_doc.name
		else:
			customer = frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")

	# -------------------------
	# Ensure Project Exists
	# -------------------------
	project = frappe.db.exists("Project", {"project_name": chat_title})

	if not project:
		project_doc = frappe.get_doc({"doctype": "Project", "project_name": chat_title})
		project_doc.insert(ignore_permissions=True)
		project = project_doc.name
	else:
		project = frappe.db.get_value("Project", {"project_name": chat_title}, "name")

	# -------------------------
	# Create Task
	# -------------------------
	task = frappe.get_doc(
		{"doctype": "Task", "subject": twitter_url, "project": project, "custom_customer": customer}
	)

	if comment_count:
		task.append("custom_interaction_metrics", {"interaction_metrics": "Comment", "count": comment_count})

	if rt_count:
		task.append("custom_interaction_metrics", {"interaction_metrics": "Retweet", "count": rt_count})

	task.insert(ignore_permissions=True)

	return {"status": "task_created", "task": task.name}


def update_task_counts(text, sender):
	# Get latest task
	task = frappe.get_all("Task", order_by="creation desc", limit=1)

	if not task:
		return {"status": "no_task"}

	task = frappe.get_doc("Task", task[0].name)

	# -------------------------
	# Ensure Supplier Exists
	# -------------------------
	supplier = frappe.db.exists("Supplier", {"supplier_name": sender})

	if not supplier:
		supplier_doc = frappe.get_doc(
			{"doctype": "Supplier", "supplier_name": sender, "supplier_type": "Individual"}
		)
		supplier_doc.insert(ignore_permissions=True)
		supplier = supplier_doc.name
	else:
		supplier = frappe.db.get_value("Supplier", {"supplier_name": sender}, "name")

	# -------------------------
	# Parse Commands
	# -------------------------
	commands = re.findall(r"(\d+)\s*(c|rt|l|qt)", text.lower())

	if not commands:
		return {"status": "no_valid_command"}

	# -------------------------
	# Create Work Log
	# -------------------------
	work_log = frappe.get_doc(
		{
			"doctype": "Task Work Log",
			"project": task.project,
			"customer": task.custom_customer,
			"task": task.name,
			"supplier": supplier,
			"task_detail": [],
		}
	)

	command_map = {"c": "Comment", "rt": "Retweet", "l": "Like", "qt": "Quote Tweet"}

	for count, cmd in commands:
		work_log.append(
			"task_detail",
			{
				"task__type": command_map.get(cmd),
				"status": "Pending",
				"count": int(count),
				"rate": 0,
				"amount": 0,
			},
		)

	work_log.insert(ignore_permissions=True)

	return {"status": "work_log_created", "task": task.name}


def handle_other_messages(text):
	frappe.log_error(text, "Other Telegram Message")

	return {"status": "ignored"}
