import frappe
from frappe.model.document import Document

# Define the PackingList class
class PackingList(Document):
    pass

@frappe.whitelist()
def get_available_items(warehouse):
    items = frappe.db.sql("""
        SELECT 
            bin.item_code, 
            item.item_name, 
            bin.actual_qty
        FROM 
            `tabBin` AS bin
        JOIN 
            `tabItem` AS item
        ON 
            bin.item_code = item.name
        WHERE 
            bin.warehouse = %s AND bin.actual_qty > 0
    """, (warehouse,), as_dict=True)  # Note the comma after warehouse for a single-element tuple
    return items