import frappe
from frappe.utils import getdate, today

def create_sales_invoice_from_packlist(doc, method):
    sales_order_ids = list(set([item.sales_order_id for item in doc.items if item.sales_order_id]))

    if not sales_order_ids:
        frappe.throw("No Sales Order linked to this Dispatch Form.")

    for sales_order_id in sales_order_ids:
        sales_order = frappe.get_doc("Sales Order", sales_order_id)

        sales_invoice = frappe.new_doc("Sales Invoice")
        sales_invoice.customer = sales_order.customer
        sales_invoice.custom_shipping_agent = sales_order.custom_shipping_agent
        sales_invoice.custom_destination = sales_order.custom_delivery_point
        sales_invoice.custom_consignee = sales_order.custom_consignee
        sales_invoice.custom_consolidated_packlist = doc.name
        sales_invoice.set_warehouse = doc.items[0].source_warehouse if doc.items else None  
        sales_invoice.posting_date = today()
        sales_invoice.update_stock = 1  # Ensure stock updates


        delivery_date = sales_order.delivery_date if sales_order.delivery_date else sales_invoice.posting_date
        sales_invoice.due_date = max(getdate(delivery_date), getdate(sales_invoice.posting_date))

        sales_invoice.taxes_and_charges = sales_order.taxes_and_charges
        sales_invoice.taxes = sales_order.taxes

        for dispatch_item in doc.items:
            if dispatch_item.sales_order_id != sales_order_id:
                continue

            so_item = next((item for item in sales_order.items if item.item_code == dispatch_item.item_code), None)

            if not so_item:
                frappe.throw(f"Item {dispatch_item.item_code} not found in Sales Order {sales_order_id}")

            item_qty = dispatch_item.bunch_qty
            if not item_qty or item_qty <= 0:
                frappe.throw(f"Invalid quantity for item {dispatch_item.item_code} in Consolidated Pack List {doc.name}")

            sales_invoice.append("items", {
                "item_code": dispatch_item.item_code,
                "qty": dispatch_item.bunch_qty,
                "uom": dispatch_item.bunch_uom,
                "bunch_qty": dispatch_item.bunch_qty,
                "bunch_uom": dispatch_item.bunch_uom,
                "custom_number_of_stems": dispatch_item.custom_number_of_stems,
                "rate": so_item.rate,
                "custom_length": so_item.custom_length,
                "discount_percentage": so_item.discount_percentage
            })

        sales_invoice.flags.ignore_permissions = True
        sales_invoice.submit()

        frappe.msgprint(f"Sales Invoice {sales_invoice.name} created from Consolidated Pack List {doc.name}")
