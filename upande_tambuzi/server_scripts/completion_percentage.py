# import frappe

# def validate_completion_percentage(doc, method):
#     total_stems = float(doc.custom_total_stems)  # Convert to float immediately
#     total_sales_order_qty = 0  # Initialize accumulator for total quantity
#     sales_orders_processed = set(
#     )  # Track processed sales orders to avoid duplicates

#     # Loop through the items to calculate total sales order quantity
#     for item in doc.items:
#         sales_order_id = item.sales_order_id

#         # Skip if we've already processed this sales order
#         if sales_order_id in sales_orders_processed:
#             continue

#         # Add to processed set
#         sales_orders_processed.add(sales_order_id)

#         # Get the corresponding Sales Order
#         sales_order = frappe.get_doc("Sales Order", sales_order_id)

#         # Fetch and accumulate the custom_total_stock_qty from the Sales Order
#         total_sales_order_qty += float(sales_order.custom_total_stock_qty)

#     # Calculate the completion percentage using totals
#     if total_sales_order_qty > 0:
#         completion_percentage = (total_stems / total_sales_order_qty) * 100
#         doc.completion_percentage = completion_percentage
#     else:
#         doc.completion_percentage = 0

#     # Log values for debugging
#     frappe.logger().debug(f"Total stems: {total_stems}")
#     frappe.logger().debug(f"Total sales order qty: {total_sales_order_qty}")
#     frappe.logger().debug(
#         f"Completion percentage: {doc.completion_percentage}")

#     # Check if the completion percentage is 100%
#     if doc.completion_percentage < 100:
#         frappe.throw(
#             "You cannot approve this Consolidated Pack List (CPL) because it is incomplete. Completion percentage must be 100%."
#         )
