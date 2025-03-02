import frappe

# Api endpoint for getting all stock entries
@frappe.whitelist(allow_guest=True)
def get_all_stock_entries_with_items():
    stock_entries = frappe.get_all("Stock Entry", fields=["name"])

    all_stock_entries_data = []

    for stock_entry in stock_entries:
        entry_doc = frappe.get_doc("Stock Entry", stock_entry.name)
        
        items = entry_doc.items

        all_stock_entries_data.append({
            "stock_entry_id": entry_doc.name,
            "items": [{
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "source_warehouse": item.s_warehouse,
                "target_warehouse": item.t_warehouse
            } for item in items]
        })
    
    return all_stock_entries_data
