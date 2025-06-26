import frappe
from frappe import _


@frappe.whitelist()
def process_failed_to_fly(cpl_name):
    try:
        cpl_doc = frappe.get_doc("Consolidated Pack List", cpl_name)

        if cpl_doc.workflow_state != "Failed To Fly":
            frappe.throw(
                _("CPL must be in 'Failed To Fly' state to process this action"
                  ))

        # Check if already processed
        if cpl_doc.get("custom_failed_to_fly_processed"):
            frappe.throw(
                _("This CPL has already been processed for Failed to Fly"))

        stock_entries_created = []

        # Process each item in the CPL
        for item_row in cpl_doc.items:
            if item_row.item_code and item_row.custom_number_of_stems:

                # Create Stock Entry
                stock_entry = frappe.new_doc("Stock Entry")
                stock_entry.stock_entry_type = "Material Transfer"
                stock_entry.company = cpl_doc.company

                # Add reference to CPL
                stock_entry.custom_reference_doctype = "Consolidated Pack List"
                stock_entry.custom_reference_name = cpl_name

                # Add item to stock entry
                stock_entry.append(
                    "items", {
                        "item_code": item_row.item_code,
                        "s_warehouse": "Delivery Truck - TL",
                        "t_warehouse": "Failed to Fly - TL",
                        "transfer_qty": item_row.custom_number_of_stems,
                        "qty": item_row.bunch_qty,
                        "uom": item_row.bunch_uom,
                    })

                # Insert and submit stock entry
                stock_entry.insert()
                stock_entry.submit()

                stock_entries_created.append(stock_entry.name)

        # Mark CPL as processed.
        cpl_doc.db_set("custom_failed_to_fly_processed",
                       1,
                       update_modified=False)

        # Add comment for audit trail
        comment = f"Failed to Fly processed. Stock Entries created: {', '.join(stock_entries_created)}"
        cpl_doc.add_comment("Info", comment)

        return {
            "success":
            True,
            "stock_entries":
            stock_entries_created,
            "message":
            f"Successfully created {len(stock_entries_created)} stock entries"
        }

    except Exception as e:
        frappe.log_error(f"Failed to Fly Error for {cpl_name}: {str(e)}")
        frappe.throw(_("Error processing Failed to Fly: {0}").format(str(e)))
