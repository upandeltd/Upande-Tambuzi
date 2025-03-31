# # # Copyright (c) 2025, Upande Limited
# # # For license information, please see license.txt

# import frappe

# @frappe.whitelist()
# def get_item_group_price(item_group, length, currency):
#     """Fetches price based on item group, length, and currency"""

#     price_doc = frappe.db.get_value("Item Group Price", {
#         "item_group": item_group,
#         "length": length,
#         "currency": currency
#     }, "price_list_rate")

#     return price_doc or 0
