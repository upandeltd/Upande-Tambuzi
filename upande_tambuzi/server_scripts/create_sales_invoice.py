import frappe
from frappe.utils import getdate, today

def create_sales_invoice_from_packlist(doc, method):
    """
    Function to create Sales Invoices from a Consolidated Pack List.
    - Handles multiple Sales Orders in one Pack List.
    - Implements error handling to prevent failures from stopping execution.
    - Sends email notifications to customers with invoice details.
    """
    sales_order_ids = list(set([item.sales_order_id for item in doc.items if item.sales_order_id]))

    if not sales_order_ids:
        frappe.throw("No Sales Order linked to this Dispatch Form.")

    created_invoices = []  #successfully created invs
    failed_invoices = []  #failed invs

    for sales_order_id in sales_order_ids:
        try:
            #SO Fetch
            sales_order = frappe.get_doc("Sales Order", sales_order_id)

            #New SI
            sales_invoice = frappe.new_doc("Sales Invoice")
            sales_invoice.customer = sales_order.customer
            sales_invoice.custom_shipping_agent = sales_order.custom_shipping_agent
            sales_invoice.custom_destination = sales_order.custom_delivery_point
            sales_invoice.custom_consignee = sales_order.custom_consignee
            sales_invoice.custom_consolidated_packlist = doc.name
            sales_invoice.set_warehouse = doc.items[0].source_warehouse if doc.items else None  
            sales_invoice.posting_date = today()
            sales_invoice.update_stock = 1  #clear stk frm system

            #Due date based on SO delivery date
            delivery_date = sales_order.delivery_date if sales_order.delivery_date else sales_invoice.posting_date
            sales_invoice.due_date = max(getdate(delivery_date), getdate(sales_invoice.posting_date))

            #Taxes frm SO
            sales_invoice.taxes_and_charges = sales_order.taxes_and_charges
            sales_invoice.taxes = sales_order.taxes

            #Process items in the Pack List that belong to the fetched SO
            for dispatch_item in doc.items:
                if dispatch_item.sales_order_id != sales_order_id:
                    continue  # Skip items not in SO

                #Find the corresponding item in SO
                so_item = next((item for item in sales_order.items if item.item_code == dispatch_item.item_code), None)

                if not so_item:
                    frappe.throw(f"Item {dispatch_item.item_code} not found in Sales Order {sales_order_id}")

                #Quantity validation
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

            #SI Create
            sales_invoice.flags.ignore_permissions = True
            sales_invoice.insert() #draft
            sales_invoice.submit() #submit
            created_invoices.append(sales_invoice.name)

        except Exception as e:
            #failed invoices.error
            failed_invoices.append(f"Sales Order {sales_order_id}: {str(e)}")

    #link to created invoices
    if created_invoices:
        invoice_links = " | ".join(
            [f'<a href="/app/sales-invoice/{invoice}" target="_blank">{invoice}</a>' for invoice in created_invoices]
        )
        frappe.msgprint(f"Sales Invoices Successfully Created: {invoice_links}", title="Sales Invoice", indicator="green")

    #error for failed invs
    if failed_invoices:
        error_message = "<br>".join(failed_invoices)
        frappe.msgprint(f"Some invoices failed to generate:<br>{error_message}", indicator="red")

    # Notify customer via email if invoices were created
    # for invoice in created_invoices:
    #     try:
    #         sales_invoice_doc = frappe.get_doc("Sales Invoice", invoice)
    #         customer_email = frappe.db.get_value("Customer", sales_invoice_doc.customer, "email_id")

    #         if customer_email:
    #             message = f"Dear {sales_invoice_doc.customer},<br><br>Your sales invoice has been generated:<br><br>"
    #             message += f'<a href="/app/sales-invoice/{invoice}" target="_blank">{invoice}</a>'

    #             frappe.sendmail(
    #                 recipients=[customer_email],
    #                 subject="Your Sales Invoice is Ready",
    #                 message=message,
    #                 attachments=[frappe.attach_print("Sales Invoice", invoice)]
    #             )
    #     except Exception as e:
    #         frappe.log_error(f"Failed to send email for Sales Invoice {invoice}: {str(e)}", "Sales Invoice Email Error")
