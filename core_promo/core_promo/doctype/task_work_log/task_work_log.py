# Copyright (c) 2026, core promo and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
BASE_URL = "https://api.x.com/2"


class TaskWorkLog(Document):
    def before_save(self):
        payment = frappe.get_doc('Payment Setting')
        total_amount=0
        for row in payment.payment_detail:
            if row.project == self.project:
                for task in self.task_detail:
                    task.rate = row.rate
                    task.amount=task.rate * task.count
                    total_amount+= task.amount
                break
        self.total_amount=total_amount
        
        

@frappe.whitelist(allow_guest=True)
def check_user_interaction(tweet_id, username):
    print("hitt")
  

    result = {
        "liked": False,
        "retweeted": False,
        "replied": False,
        "quoted": False
    }

    # 1️⃣ Get user id
    user_url = f"{BASE_URL}/users/by/username/{username}"
    r = requests.get(user_url)
    if r.status_code != 200:
        return {"error": "User not found"}

    user_id = r.json()["data"]["id"]

    # 2️⃣ Check likes
    like_url = f"{BASE_URL}/tweets/{tweet_id}/liking_users"
    r = requests.get(like_url)

    if r.status_code == 200:
        users = r.json().get("data", [])
        for u in users:
            if u["id"] == user_id:
                result["liked"] = True

    # 3️⃣ Check retweets
    rt_url = f"{BASE_URL}/tweets/{tweet_id}/retweeted_by"
    r = requests.get(rt_url)

    if r.status_code == 200:
        users = r.json().get("data", [])
        for u in users:
            if u["id"] == user_id:
                result["retweeted"] = True

    # 4️⃣ Check replies
    reply_url = f"{BASE_URL}/tweets/search/recent?query=conversation_id:{tweet_id}&tweet.fields=author_id"
    r = requests.get(reply_url)

    if r.status_code == 200:
        tweets = r.json().get("data", [])
        for t in tweets:
            if t["author_id"] == user_id:
                result["replied"] = True

    # 5️⃣ Check quote tweets
    quote_url = f"{BASE_URL}/tweets/{tweet_id}/quote_tweets?tweet.fields=author_id"
    r = requests.get(quote_url)

    if r.status_code == 200:
        tweets = r.json().get("data", [])
        for t in tweets:
            if t["author_id"] == user_id:
                result["quoted"] = True
    print("end")
    return result


import frappe
import requests

BASE_URL = "https://api.x.com/2"


def get_headers():
    return {
        "Authorization": f"Bearer {frappe.conf.x_bearer_token}"
    }


@frappe.whitelist()
def check_user_interaction(tweet_id, username):

    headers = get_headers()

    result = {
        "liked": False,
        "retweeted": False,
        "replied": False,
        "quoted": False
    }

    try:

        # 1️⃣ Get user ID
        user_url = f"{BASE_URL}/users/by/username/{username}"
        r = requests.get(user_url, headers=headers, timeout=10)

        if r.status_code != 200:
            return {"error": "User not found"}

        user_id = r.json().get("data", {}).get("id")

        # 2️⃣ Check Likes
        like_url = f"{BASE_URL}/tweets/{tweet_id}/liking_users"
        r = requests.get(like_url, headers=headers, timeout=10)

        if r.status_code == 200:
            users = r.json().get("data", [])
            result["liked"] = any(u["id"] == user_id for u in users)

        # 3️⃣ Check Retweets
        rt_url = f"{BASE_URL}/tweets/{tweet_id}/retweeted_by"
        r = requests.get(rt_url, headers=headers, timeout=10)

        if r.status_code == 200:
            users = r.json().get("data", [])
            result["retweeted"] = any(u["id"] == user_id for u in users)

        # 4️⃣ Check Replies
        reply_url = f"{BASE_URL}/tweets/search/recent?query=conversation_id:{tweet_id}&tweet.fields=author_id"
        r = requests.get(reply_url, headers=headers, timeout=10)

        if r.status_code == 200:
            tweets = r.json().get("data", [])
            result["replied"] = any(t["author_id"] == user_id for t in tweets)

        # 5️⃣ Check Quotes
        quote_url = f"{BASE_URL}/tweets/{tweet_id}/quote_tweets?tweet.fields=author_id"
        r = requests.get(quote_url, headers=headers, timeout=10)

        if r.status_code == 200:
            tweets = r.json().get("data", [])
            result["quoted"] = any(t["author_id"] == user_id for t in tweets)

    except Exception as e:
        frappe.log_error(str(e), "X Interaction Check Error")
        return {"error": "API Error"}

    return result

import frappe
import frappe
import frappe
@frappe.whitelist()
def create_purchase_invoice():

    records = frappe.get_all(
        "Task Work Log",
        filters={"docstatus": 0},
        fields=["name", "supplier"]
    )

    if not records:
        return "No unpaid records found"

    supplier_map = {}

    for row in records:
        if not row.supplier:
            frappe.throw(f"Supplier missing in Task Work Log {row.name}")

        supplier_map.setdefault(row.supplier, []).append(row.name)

    created_invoices = []

    for supplier, task_names in supplier_map.items():

        pi = frappe.new_doc("Purchase Invoice")
        pi.supplier = supplier
        pi.company = frappe.defaults.get_user_default("Company")

        for task in task_names:

            doc = frappe.get_doc("Task Work Log", task)

            for d in doc.task_detail:
                pi.append("items", {
                    "item_code":"SERVICE-ITEM",
                    "qty": d.count,
                    "rate": d.rate,
                    "custom_task": task
                })
        print("hitt",pi)
        pi.insert(ignore_permissions=True)
        pi.submit()

        created_invoices.append(pi.name)

        for task in task_names:
            frappe.db.set_value("Task Work Log", task, "docstatus", 1)

    frappe.db.commit()

    return created_invoices