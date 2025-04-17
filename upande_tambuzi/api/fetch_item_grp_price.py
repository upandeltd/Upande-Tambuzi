# Copyright (c) 2025, Upande Limited
# For license information, please see license.txt

# This function fetches the price for a given item group, length, and currency from the Item Group Price table.

import frappe
from frappe import _

@frappe.whitelist(allow_guest=False)
def fetch_item_grp_price():
    # Fetch parameters from the request
    item_group = frappe.form_dict.get("item_group")
    length = frappe.form_dict.get("length")
    currency = frappe.form_dict.get("currency")

    # Log the received parameters
    frappe.logger().info(f"Fetching price for item_group: {item_group}, length: {length}, currency: {currency}")
    print(f"Fetching price for item_group: {item_group}, length: {length}, currency: {currency}")  # Debug print

    # Validate required parameters
    if not item_group or not length or not currency:
        frappe.logger().warning("Missing required parameters")
        print("Missing required parameters")  # Debug print
        frappe.response["message"] = "Missing required parameters"
        return

    # Fetch the price from the database
    price_doc = frappe.db.get_value(
        "Item Group Price",
        {"item_group": item_group, "length": length, "currency": currency},
        "price_list_rate"
    )

    # Log the fetched price
    frappe.logger().info(f"Fetched price: {price_doc}")
    print(f"Fetched price: {price_doc}")

    frappe.response["message"] = price_doc if price_doc else None
