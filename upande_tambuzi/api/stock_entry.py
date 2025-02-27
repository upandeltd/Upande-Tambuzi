import frappe

@frappe.whitelist(allow_guest=True)
def get_stock_entry_items(stock_entry_id):
    if not stock_entry_id:
        frappe.throw("Stock Entry ID is required")

    stock_entry = frappe.get_doc("Stock Entry", stock_entry_id)
    
    items = stock_entry.get("items")
    
    return [{
        "item_code": item.item_code,
        "qty": item.qty,
        "uom": item.uom,
        "source_warehouse": item.s_warehouse,
        "target_warehouse": item.t_warehouse
    } for item in items]
