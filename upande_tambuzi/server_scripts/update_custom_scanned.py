import frappe

@frappe.whitelist()
def update_custom_scanned(stock_entry_name):
    stock_entry = frappe.get_doc("Stock Entry", stock_entry_name)
    if stock_entry.docstatus == 1:
        stock_entry.db_set("custom_scanned", 1)
        frappe.db.commit()