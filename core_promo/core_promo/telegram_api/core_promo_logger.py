import frappe


@frappe.whitelist(allow_guest=True)
def telegram_webhook():
	try:
		raw_data = frappe.request.data

		# convert bytes → string
		if isinstance(raw_data, bytes):
			raw_data = raw_data.decode("utf-8")

		# log raw telegram payload
		frappe.log_error(raw_data, "Telegram Webhook Raw Data")

		return {"status": "received"}

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Telegram Webhook Error")
		return {"status": "error"}
