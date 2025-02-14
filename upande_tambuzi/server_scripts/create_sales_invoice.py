import frappe

@frappe.whitelist()
def create_sales_invoice(doc, method):
    """Triggered when a Consolidated Pack List is submitted"""

    # Ensure there's at least one item row in the Consolidated Pack List
    if not doc.items or len(doc.items) == 0:
        frappe.throw("No items found in the Consolidated Pack List.")

    # Fetch the customer ID from the first row of the items table
    customer_id = doc.items[0].customer_id if hasattr(doc.items[0], "customer_id") else None

    # Fetch source warehouse from the first row of the items table
    source_warehouse = doc.items[0].source_warehouse if hasattr(doc.items[0], "source_warehouse") else None

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
        "status": "Draft",
        "set_warehouse": source_warehouse  # Set warehouse for the entire invoice
    })

    # Add Items from Consolidated Pack List
    for item in doc.items:
        sales_invoice.append("items", {
            "item_code": item.item_code,
            "uom": item.uom,
            "qty": item.qty,
            "rate": item.rate or 0,
            "amount": item.qty * (item.rate or 0),
            "warehouse": item.source_warehouse,
             "custom_length": item.length
        })

    # Insert Sales Invoice in Draft
    sales_invoice.insert(ignore_permissions=True)

    # Notify User
    frappe.msgprint(f"Sales Invoice {sales_invoice.name} created successfully.", alert=True)

    return sales_invoice.name
