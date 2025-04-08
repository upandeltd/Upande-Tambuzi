import frappe
from frappe.utils import nowdate

# Map source to reserve warehouses
WAREHOUSE_MAPPING = {
    "Pendekeza Available for Sale - TL": "Pendekeza Graded Reserve - TL",
    "Turaco Available for Sale - TL": "Turaco Graded Reserve - TL",
    "Burguret Available for Sale - TL": "Burguret Graded Reserve - TL"
}


@frappe.whitelist()
def reserve_stock(sales_order):
    doc = frappe.get_doc("Sales Order", sales_order)

    is_priority = frappe.db.get_value("Customer", doc.customer,
                                      "custom_priority_customer")
    if not is_priority:
        frappe.throw(
            "Stock Reservation is only allowed for priority customers.")

    items = []
    messages = []

    for item in doc.items:
        source_warehouse = item.custom_source_warehouse
        target_warehouse = WAREHOUSE_MAPPING.get(source_warehouse)

        if not target_warehouse:
            continue

        items.append({
            "item_code": item.item_code,
            "qty": item.qty,
            "uom": item.uom,
            "s_warehouse": source_warehouse,
            "t_warehouse": target_warehouse
        })

        messages.append(
            f" <b>{item.item_name}: {item.stock_qty} </b> from <b>{source_warehouse}</b> to <b>{target_warehouse}</b>"
        )

    if not items:
        frappe.throw("No valid items found for reservation.")

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.company = doc.company
    stock_entry.posting_date = nowdate()
    #stock_entry.set_stock_entry_type()
    stock_entry.items = []

    for i in items:
        stock_entry.append("items", i)

    stock_entry.custom_linked_sales_order = sales_order  # Optional: link
    stock_entry.insert(ignore_permissions=True)
    stock_entry.submit()

    return "<br>".join(messages + [
        f"<br><b>Stock Reserved Successfully in Stock Entry:</b> <a href='/app/stock-entry/{stock_entry.name}'>{stock_entry.name}</a>"
    ])


@frappe.whitelist()
def unreserve_stock(sales_order):
    doc = frappe.get_doc("Sales Order", sales_order)

    items = []
    messages = []

    for item in doc.items:
        source_warehouse = WAREHOUSE_MAPPING.get(item.custom_source_warehouse)
        target_warehouse = item.custom_source_warehouse

        if not source_warehouse:
            continue

        items.append({
            "item_code": item.item_code,
            "qty": item.qty,
            "uom": item.uom,
            "s_warehouse": source_warehouse,
            "t_warehouse": target_warehouse
        })

        messages.append(
            f" <b>{item.item_name}: {item.stock_qty} </b> from <b>{source_warehouse}</b> to <b>{target_warehouse}</b>"
        )

    if not items:
        frappe.throw("No valid items found for unreserving.")

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.company = doc.company
    stock_entry.posting_date = nowdate()
    #stock_entry.set_stock_entry_type()
    stock_entry.items = []

    for i in items:
        stock_entry.append("items", i)

    stock_entry.custom_linked_sales_order = sales_order
    stock_entry.insert(ignore_permissions=True)
    stock_entry.submit()

    return "<br>".join(messages + [
        f"<br><b>Stock Unreserved Successfully in Stock Entry:</b> <a href='/app/stock-entry/{stock_entry.name}'>{stock_entry.name}</a>"
    ])
