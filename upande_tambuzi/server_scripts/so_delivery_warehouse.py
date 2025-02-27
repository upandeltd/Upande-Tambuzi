import frappe


def handle_sales_order_approval(doc, method):
    warehouse_mapping = {
        "Turaco Graded General - TL": "Turaco Graded Sold - TL",
        "Pendekeza Graded General - TL": "Pendekeza Graded Sold - TL",
        "Burguret Graded General - TL": "Burguret Graded Sold - TL"
    }

    updated = False
    for item in doc.items:
        if item.custom_source_warehouse:
            mapped_warehouse = warehouse_mapping.get(
                item.custom_source_warehouse, "")
            if mapped_warehouse and item.warehouse != mapped_warehouse:
                item.warehouse = mapped_warehouse
                updated = True

    if updated:
        doc.save()
        frappe.msgprint(
            "Delivery warehouse updated based on Source Warehouse.")

    if doc.docstatus == 1:
        # Create Material Transfer Entry
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.sales_order = doc.name  # Link to Sales Order

        for item in doc.items:
            if item.custom_source_warehouse and item.warehouse:
                stock_entry.append(
                    "items",
                    {
                        "item_code": item.item_code,
                        "qty": item.qty,
                        "uom": item.uom,
                        "stock_uom": item.stock_uom,
                        "s_warehouse": item.custom_source_warehouse,
                        "t_warehouse": item.warehouse,
                        "stock_qty": item.stock_qty,
                    },
                )

        if stock_entry.items:
            stock_entry.insert()
            stock_entry.submit()
            frappe.msgprint("Stock Transfer Created Successfully!")

    else:

        #frappe.msgprint(
        # "Sales Order not approved. Stock Transfer not created.")
        pass
