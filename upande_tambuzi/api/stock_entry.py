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
            "stock_entry_type": entry_doc.stock_entry_type,
            "posting_date": entry_doc.posting_date,
            "posting_time": entry_doc.posting_time,
            "farm": entry_doc.custom_farm,
            "greenhouse": entry_doc.custom_greenhouse,
            "bed_number": entry_doc.custom_block__bed_number,
            "harvester_payroll_no": entry_doc.custom_harvester_payroll_number,
            "items": [{
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "source_warehouse": item.s_warehouse,
                "target_warehouse": item.t_warehouse
            } for item in items]
        })
    
    return all_stock_entries_data
