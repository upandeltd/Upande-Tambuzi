import frappe
from frappe.model.document import Document


def on_submit_sales_order(doc, method):
    if doc.workflow_state != "Approved":
        return

    warehouse_patterns = [{
        "from": "Graded General",
        "to": "Graded Sold"
    }, {
        "from": "Dispatch Form",
        "to": "Dispatch Sold"
    }]

    stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Transfer",
        "items": []
    })

    for item in doc.items:
        source_warehouse = item.custom_source_warehouse
        target_warehouse = None

        # Try each pattern until we find a match
        for pattern in warehouse_patterns:
            if pattern["from"] in source_warehouse:
                target_warehouse = source_warehouse.replace(
                    pattern["from"], pattern["to"])
                break

        if not target_warehouse:
            frappe.throw(
                f"Could not determine target warehouse for source warehouse '{source_warehouse}'. No matching pattern found."
            )

        # Verify target warehouse exists
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
