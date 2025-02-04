import frappe
from frappe.model.document import Document

class SalesOrder(Document):
    def on_submit(self):
        create_stock_transfer(self)

def create_stock_transfer(doc, *args, **kwargs):
    """Automatically creates a Stock Entry when a Sales Order is submitted."""
    source_warehouse = "Graded General Store"
    target_warehouse = "Graded Sold Store"

    if not doc.items:
        frappe.throw("No items found in the Sales Order.")

    # Create a new Stock Entry
    stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Transfer",
        "sales_order": doc.name,  # Link Stock Entry to Sales Order
        "items": []
    })

    for item in doc.items:
        stock_entry.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "uom": item.uom,
            "stock_uom": item.stock_uom,
            "s_warehouse": source_warehouse,
            "t_warehouse": target_warehouse
        })

    stock_entry.insert()
    stock_entry.submit()

    frappe.msgprint(f"Stock transferred to {target_warehouse} for Sales Order {doc.name}")
