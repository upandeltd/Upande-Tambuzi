# Copyright (c) 2025, Upande Limited and contributors
# For license information, please see license.txt


import frappe

@frappe.whitelist()
def get_item_group_price(item_group=None, length=None):
    if not item_group or not length:
        return 0  # Return 0 if required fields are missing

    price = frappe.db.get_value(
        "Item Group Price",
        {"item_group": item_group, "length": length},
        "price_list_rate",
    )
    
    return price or 0  # Return 0 if no price is found
