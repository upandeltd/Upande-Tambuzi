import frappe

def create_sales_invoice(doc, method):
    """
    This function triggers when a Dispatch Form is submitted.
    It fetches relevant Sales Order details and creates a Sales Invoice.
    """
    sales_order_ids = list(set([item.sales_order_id for item in doc.custom_sku_summary if item.sales_order_id]))

    if not sales_order_ids:
        frappe.throw("No Sales Order linked to this Dispatch Form.")

    for sales_order_id in sales_order_ids:
        sales_order = frappe.get_doc("Sales Order", sales_order_id)

        # Create a new Sales Invoice in Draft mode
        sales_invoice = frappe.new_doc("Sales Invoice")
        sales_invoice.customer = sales_order.customer
        sales_invoice.due_date = sales_order.delivery_date or frappe.utils.nowdate()
        sales_invoice.custom_dispatch_form = doc.name  # Link Dispatch Form

        # Copy taxes and discounts from Sales Order
        sales_invoice.taxes_and_charges = sales_order.taxes_and_charges
        sales_invoice.taxes = sales_order.taxes  # Copy all tax details

        # Process Dispatch Form Items
        for dispatch_item in doc.custom_sku_summary:
            if dispatch_item.sales_order_id != sales_order_id:
                continue  # Skip items not linked to the current Sales Order

            # Find matching item from Sales Order
            so_item = next((item for item in sales_order.items if item.item_code == dispatch_item.item_code), None)
            if not so_item:
                frappe.throw(f"Item {dispatch_item.item_code} not found in Sales Order {sales_order_id}")

            # Append item to Sales Invoice
            sales_invoice.append("items", {
                "item_code": dispatch_item.item_code,
                "bunch_qty": dispatch_item.bunch_qty,
                "bunch_uom": dispatch_item.bunch_uom,
                "no_of_stems": dispatch_item.no_of_stems,
                # "stock_uom": dispatch_item.stock_uom,
                "rate": so_item.rate, 
                "custom_length": so_item.custom_length, 
                "discount_percentage": so_item.discount_percentage,  
                "source_warehouse": dispatch_item.source_warehouse 
            })

        # Save the Sales Invoice as Draft
        sales_invoice.flags.ignore_permissions = True
        sales_invoice.insert()
        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created from Dispatch Form {doc.name}")
