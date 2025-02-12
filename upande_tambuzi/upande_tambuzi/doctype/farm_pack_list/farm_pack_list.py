import frappe
from frappe import _
from frappe.model.document import Document

class FarmPackList(Document):
    pass

@frappe.whitelist()
def close_farm_pack_list(farm_pack_list):
    # Check if user has write permission for Farm Pack List
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to close Farm Pack List"))
        
    doc = frappe.get_doc("Farm Pack List", farm_pack_list)
    if doc.custom_status == "Closed":
        frappe.throw(_("Farm Pack List is already closed"))
    
    doc.db_set('custom_status', 'Closed', update_modified=False)
    doc.notify_update()
    frappe.db.commit()
    return True

@frappe.whitelist()
def process_consolidated_pack_list(farm_pack_list, sales_order_id=None):
    # Check permissions for both doctypes
    if not frappe.has_permission("Farm Pack List", "read"):
        frappe.throw(_("Not permitted to read Farm Pack List"))
    if not frappe.has_permission("Consolidated Pack List", "write"):
        frappe.throw(_("Not permitted to create/modify Consolidated Pack List"))

    farm_pack_doc = frappe.get_doc("Farm Pack List", farm_pack_list)

    # Determine Sales Order ID from Farm Pack List items if not provided
    if not sales_order_id:
        if farm_pack_doc.pack_list_item:
            sales_order_id = farm_pack_doc.pack_list_item[0].sales_order_id  

    if not sales_order_id:
        frappe.throw(_("Sales Order ID is required to process the Consolidated Pack List."))

    # Check if a CPL already exists for the Sales Order
    existing_cpl = frappe.get_all(
        "Consolidated Pack List",
        filters={"sales_order_id": sales_order_id},
        fields=["name"],
        limit=1
    )

    try:
        if existing_cpl:
            frappe.msgprint(_("Updating existing CPL: {0}").format(existing_cpl[0]["name"]))
            cpl = frappe.get_doc("Consolidated Pack List", existing_cpl[0]["name"])
            
            # Check if user has write permission for existing CPL
            if not cpl.has_permission("write"):
                frappe.throw(_("Not permitted to modify this Consolidated Pack List"))
        else:
            frappe.msgprint(_("Creating new CPL"))
            cpl = frappe.new_doc("Consolidated Pack List")
            cpl.sales_order_id = sales_order_id

            # Fetch customer_id from the first item in the child table
            if farm_pack_doc.pack_list_item:
                cpl.customer_id = farm_pack_doc.pack_list_item[0].customer_id
            else:
                frappe.throw(_("No items found in the Farm Pack List. Cannot process CPL."))

        # Ensure CPL has an 'items' field
        if "items" not in cpl.as_dict():
            frappe.throw(_("Field 'items' does not exist in Consolidated Pack List"))

        # Append items from the Farm Pack List's child table
        for item in farm_pack_doc.pack_list_item:
            cpl.append("items", {
                "source_warehouse": item.source_warehouse,
                "customer_id": item.customer_id,
                "sales_order_id": item.sales_order_id,
                "box_id": item.box_id,
                "item_code": item.item_code,
                "uom": item.uom,
                "qty": item.qty,
                "custom_rate":item.custom_rate
            })
        
        # Save the CPL in Draft mode (docstatus=0)
        cpl.save()
        frappe.msgprint(_("CPL Created in Draft: {0}").format(cpl.name))

        frappe.db.commit()
        return cpl.name

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(f"Error processing CPL: {str(e)}")
        frappe.throw(_("Error processing Consolidated Pack List: {0}").format(str(e)))