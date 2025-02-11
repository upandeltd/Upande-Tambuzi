# Copyright (c) 2025, Upande Limited and contributors
# For license information, please see license.txt

import frappe

@frappe.whitelist()
def get_item_group_price():
    # Initialize default price as 0
    price_doc = 0
    if frappe.form_dict:
        data = frappe.form_dict
        # Fetch the custom price from Item Group Price
        price_doc = frappe.db.get_value(
            "Item Group Price",
            {
                "item_group": data.get('item_group'),
                "length": data.get('length'),
            },
            "price_list_rate",
        )
    
    # Return price or default to 0
    frappe.response['message'] = price_doc or 0
