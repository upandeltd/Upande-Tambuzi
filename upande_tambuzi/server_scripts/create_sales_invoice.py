import frappe

@frappe.whitelist()
def create_sales_invoice(doc, method):
    """Triggered when a Consolidated Pack List is submitted"""

    # Ensure there's at least one item row in the Consolidated Pack List
    if not doc.items or len(doc.items) == 0:
        frappe.throw("No items found in the Consolidated Pack List.")

    # Fetch the customer ID from the first row of the items table
    customer_id = doc.items[0].customer_id if hasattr(doc.items[0], "customer_id") else None

    # Validate if Customer ID is found
    if not customer_id:
        frappe.throw("Customer is missing in the Consolidated Pack List items. Please select a customer.")

    # Check if Sales Invoice already exists
    if frappe.db.exists("Sales Invoice", {"custom_consolidated_packlist": doc.name}):
        frappe.msgprint("Sales Invoice already exists for this Consolidated Pack List.", alert=True)
        return

    # Create Sales Invoice
    sales_invoice = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": customer_id,  # Fetch customer ID from child table
        "posting_date": frappe.utils.today(),
        "due_date": frappe.utils.add_days(frappe.utils.today(), 30),
        "items": [],
        "custom_consolidated_packlist": doc.name,
        "status": "Draft"
    })

    # Add Items from Consolidated Pack List
    for item in doc.items:
        sales_invoice.append("items", {
            "item_code": item.item_code,
            "uom": item.uom,
            "qty": item.qty,
            "rate": item.custom_rate or 0,
            "amount": item.qty * (item.custom_rate or 0),
        })

    # Insert Sales Invoice in Draft
    sales_invoice.insert(ignore_permissions=True)

    # Notify User
    frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully.", alert=True)

    return sales_invoice.name
