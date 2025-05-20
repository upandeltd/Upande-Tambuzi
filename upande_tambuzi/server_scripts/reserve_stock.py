# import frappe
# from frappe.utils import nowdate

# # Map source to reserve warehouses
# WAREHOUSE_MAPPING = {
#     "Pendekeza Available for Sale - TL": "Pendekeza Graded Reserve - TL",
#     "Turaco Available for Sale - TL": "Turaco Graded Reserve - TL",
#     "Burguret Available for Sale - TL": "Burguret Graded Reserve - TL"
# }

# @frappe.whitelist()
# def create_or_update_stock_entry(sales_order, is_draft=True):
#     doc = frappe.get_doc("Sales Order", sales_order)

#     items = []
#     messages = []

#     for item in doc.items:
#         source_warehouse = item.custom_source_warehouse
#         target_warehouse = WAREHOUSE_MAPPING.get(source_warehouse)

#         if not target_warehouse:
#             continue

#         items.append({
#             "item_code": item.item_code,
#             "qty": item.qty,
#             "uom": item.uom,
#             "s_warehouse": source_warehouse,
#             "t_warehouse": target_warehouse
#         })

#         messages.append(
#             f"<b>{item.item_name}: {item.stock_qty}</b> from <b>{source_warehouse}</b> to <b>{target_warehouse}</b>"
#         )

#     if not items:
#         frappe.throw("No valid items found for reservation.")

#     # Cancel existing stock entry if exists
#     existing_stock_entry = frappe.db.get_value(
#         "Stock Entry",
#         {
#             "custom_linked_sales_order": sales_order,
#             "docstatus": 1  # Only cancel if submitted
#         },
#         ["name"])

#     if existing_stock_entry:
#         try:
#             old_entry = frappe.get_doc("Stock Entry", existing_stock_entry)
#             old_entry.cancel()
#         except Exception as e:
#             frappe.log_error(
#                 f"Failed to cancel Stock Entry {existing_stock_entry}: {str(e)}"
#             )
#             frappe.throw(
#                 f"Failed to cancel existing stock reservation: {str(e)}")

#     # Create new stock entry
#     stock_entry = frappe.new_doc("Stock Entry")
#     stock_entry.stock_entry_type = "Material Transfer"
#     stock_entry.company = doc.company
#     stock_entry.posting_date = nowdate()
#     stock_entry.custom_linked_sales_order = sales_order

#     for i in items:
#         stock_entry.append("items", i)

#     stock_entry.insert(ignore_permissions=True)
#     stock_entry.submit()

#     doc.db_set("custom_is_reserved", 1)

#     frappe.msgprint(
#         msg=
#         f"Stock Reserved Successfully in Stock Entry: <a href='/app/stock-entry/{stock_entry.name}'>{stock_entry.name}</a><br>"
#         + "<br>".join(messages),
#         title="Stock Reservation",
#         indicator="green")

# def unreserve_stock(sales_order):
#     """Create stock entry to unreserve stock when sales order is approved."""
#     doc = frappe.get_doc("Sales Order", sales_order)

#     items = []
#     messages = []

#     for item in doc.items:
#         source_warehouse = WAREHOUSE_MAPPING.get(item.custom_source_warehouse)
#         target_warehouse = item.custom_source_warehouse

#         if not source_warehouse:
#             continue

#         items.append({
#             "item_code": item.item_code,
#             "qty": item.qty,
#             "uom": item.uom,
#             "s_warehouse": source_warehouse,
#             "t_warehouse": target_warehouse
#         })

#         messages.append(
#             f"<b>{item.item_name}: {item.stock_qty}</b> from <b>{source_warehouse}</b> to <b>{target_warehouse}</b>"
#         )

#     if not items:
#         frappe.throw("No valid items found for unreserving.")

#     # Cancel existing stock reservation if any
#     existing_stock_entry = frappe.db.get_value("Stock Entry", {
#         "custom_linked_sales_order": sales_order,
#         "docstatus": 1
#     }, ["name"])
#     if existing_stock_entry:
#         try:
#             stock_entry = frappe.get_doc("Stock Entry", existing_stock_entry)
#             stock_entry.cancel()
#         except Exception as e:
#             frappe.log_error(
#                 f"Failed to cancel Stock Entry {existing_stock_entry}: {str(e)}"
#             )
#             frappe.throw(
#                 f"Failed to cancel existing stock reservation: {str(e)}")

#     # Create new stock entry for unreservation
#     stock_entry = frappe.new_doc("Stock Entry")
#     stock_entry.stock_entry_type = "Material Transfer"
#     stock_entry.company = doc.company
#     stock_entry.posting_date = nowdate()
#     stock_entry.custom_linked_sales_order = sales_order
#     for i in items:
#         stock_entry.append("items", i)

#     try:
#         stock_entry.insert(ignore_permissions=True)
#         stock_entry.submit()
#     except Exception as e:
#         frappe.log_error(
#             f"Failed to create unreservation Stock Entry for Sales Order {sales_order}: {str(e)}"
#         )
#         frappe.throw(f"Failed to unreserve stock: {str(e)}")

#     frappe.msgprint(
#         msg=
#         f"Stock Unreserved Successfully in Stock Entry: <a href='/app/stock-entry/{stock_entry.name}'>{stock_entry.name}</a><br>"
#         + "<br>".join(messages),
#         title="Stock Unreservation",
#         indicator="green")

# def on_sales_order_save(doc, method):
#     """Hook to create stock entry when sales order is saved."""
#     if doc.workflow_state == "Draft":
#         create_or_update_stock_entry(doc.name)

# def on_sales_order_update(doc, method):
#     """Hook to update stock entry when sales order is updated in draft."""
#     if doc.docstatus == 0:  # Draft
#         create_or_update_stock_entry(doc.name, is_draft=True)

# def on_sales_order_approved(doc, method):
#     """Hook to unreserve stock when sales order is approved and submitted."""
#     if doc.workflow_state == "Approved":
#         try:
#             unreserve_stock(doc.name)
#         except Exception as e:
#             frappe.log_error(
#                 f"Unreservation failed for Sales Order {doc.name}: {str(e)}")
#             frappe.throw(f"Failed to unreserve stock: {str(e)}")
