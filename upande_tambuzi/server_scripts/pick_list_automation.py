import frappe

def auto_create_pick_list_on_sales_order_submit(doc, method):
    # Check if the Sales Order has items
    if doc.items:
        # Create a new Pick List document
        pick_list = frappe.get_doc(dict(
            doctype='Pick List',
            reference_name=doc.name,  # Link the Pick List to the Sales Order
            items=[
                {
                    "item_code": item.item_code,
                    "quantity": item.qty,
                    "uom": item.uom,
                    "warehouse": item.warehouse
                } for item in doc.items  # Map items from the Sales Order
            ]
        ))

        pick_list.insert()
        pick_list.submit()
