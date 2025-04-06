# import frappe
# from frappe import _

# def before_cancel(self):
#     # Collect all Sales Orders from the current Farm Pack List (FPL)
#     fpl_sales_orders = [
#         row.sales_order_id for row in self.pack_list_item if row.sales_order_id
#     ]

#     if not fpl_sales_orders:
#         return  # No sales orders linked, safe to cancel

#     # Find any Consolidated Pack List (CPL) that includes the same sales orders
#     cpl_records = frappe.db.get_all(
#         "Dispatch Form Item",
#         filters={"sales_order_id": ["in", fpl_sales_orders]},
#         fields=["parent"])

#     if cpl_records:
#         # Get the first matching CPL ID (you can list all if needed)
#         cpl_ids = [record.parent for record in cpl_records]
#         cpl_id_str = ", ".join(cpl_ids)

#         # Block cancellation and show message
#         frappe.throw(
#             _(f"Cancel {cpl_id_str} before cancelling this Farm Pack List."),
#             title="Cannot Cancel")
