import frappe
from frappe.model.document import Document


def on_submit_sales_order(doc, method):
    if doc.workflow_state != "Approved":
        return

    stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Transfer",
        "items": []
    })

    for item in doc.items:
        source_warehouse = item.custom_source_warehouse
        target_warehouse = item.warehouse  # Assuming you have a target warehouse field

        if not source_warehouse:
            frappe.throw(
                f"Source warehouse is required for item {item.item_code}")

        if not target_warehouse:
            frappe.throw(
                f"Target warehouse is required for item {item.item_code}")

        # Verify warehouses exist
        if not frappe.db.exists("Warehouse", source_warehouse):
            frappe.throw(
                f"Source warehouse '{source_warehouse}' does not exist")
        if not frappe.db.exists("Warehouse", target_warehouse):
            frappe.throw(
                f"Target warehouse '{target_warehouse}' does not exist")

        stock_entry.append(
            "items", {
                "item_code": item.item_code,
                "item_group": item.item_group,
                "qty": item.qty,
                "uom": item.uom,
                "length": item.custom_length,
                "no_of_stems": item.stock_qty,
                "stock_uom": item.stock_uom,
                "rate": item.rate,
                "amount": item.amount,
                "s_warehouse": source_warehouse,
                "t_warehouse": target_warehouse
            })

    stock_entry.insert()
    stock_entry.submit()
