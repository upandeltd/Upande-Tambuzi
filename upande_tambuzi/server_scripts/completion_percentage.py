# import frappe

# def validate_completion_percentage(doc, method):
#     # Fetch the Sales Order ID from the child table
#     for item in doc.items:
#         sales_order_id = item.sales_order_id

#         # Get the corresponding Sales Order
#         sales_order = frappe.get_doc("Sales Order", sales_order_id)

#         # Fetch the custom_total_stock_qty from the Sales Order
#         sales_order_qty = sales_order.custom_total_stock_qty

#         # Calculate the total stems from the CPL item row
#         cpl_total_stems = custom_total_stems

#         # Calculate the completion percentage
#         completion_percentage = (cpl_total_stems / sales_order_qty) * 100

#         # Update the completion_percentage field in the CPL
#         item.completion_percentage = completion_percentage

#     # After iterating over the items, check if the completion percentage is 100%
#     if any(item.completion_percentage < 100 for item in doc.items):
#         frappe.throw("You cannot approve this Consolidated Pack List (CPL) because it is incomplete. Completion percentage must be 100%.")
