import frappe


@frappe.whitelist()
def reserve_stems(item_code, custom_source_warehouse, stems_requested):
    stems_requested = int(stems_requested)

    # Determine destination: Graded Reserve warehouse
    farm = custom_source_warehouse.split(" ")[0]
    graded_reserve_warehouse = f"{farm} Graded Reserve - TL"

    bin_data = frappe.get_value("Bin", {
        "item_code": item_code,
        "warehouse": custom_source_warehouse
    }, ["actual_qty", "reserved_qty"],
                                as_dict=True)

    if not bin_data:
        return {
            "reserved_qty":
            0,
            "status":
            "Not Found",
            "message":
            f"No stock found for {item_code} in {custom_source_warehouse}."
        }

    available_stems = max(0, bin_data.actual_qty - bin_data.reserved_qty)
    stems_to_reserve = min(available_stems, stems_requested)

    if stems_to_reserve > 0:
        frappe.db.set_value("Bin", {
            "item_code": item_code,
            "warehouse": custom_source_warehouse
        }, "reserved_qty", bin_data.reserved_qty + stems_to_reserve)

    return {
        "reserved_qty":
        stems_to_reserve,
        "status":
        "Reserved" if stems_to_reserve > 0 else "Insufficient Stock",
        "message":
        f"{'Reserved' if stems_to_reserve > 0 else 'Could not reserve'} {stems_to_reserve} stems for {item_code} from {custom_source_warehouse}."
    }


# @frappe.whitelist()
# def unreserve_on_row_delete(item_code, custom_source_warehouse, reserved_qty):
#     reserved_qty = int(reserved_qty)

#     if not item_code or not custom_source_warehouse:
#         return {
#             "status": "Error",
#             "message": "Missing item_code or custom_source_warehouse."
#         }

#     bin_data = frappe.get_value("Bin", {
#         "item_code": item_code,
#         "warehouse": custom_source_warehouse
#     }, ["reserved_qty"],
#                                 as_dict=True)

#     if not bin_data:
#         return {
#             "status":
#             "Not Found",
#             "message":
#             f"No bin record found for {item_code} in {custom_source_warehouse}."
#         }

#     new_reserved_qty = max(0, bin_data.reserved_qty - reserved_qty)

#     frappe.db.set_value("Bin", {
#         "item_code": item_code,
#         "warehouse": custom_source_warehouse
#     }, "reserved_qty", new_reserved_qty)

#     return {
#         "status": "Unreserved",
#         "message":
#         f"Unreserved {reserved_qty} stems for {item_code} from {custom_source_warehouse}.",
#         "new_reserved_qty": new_reserved_qty
#     }

# def on_sales_order_item_delete(doc, method):
#     """Handle unreserving when a Sales Order Item is deleted"""
#     try:
#         if doc.item_code and hasattr(
#                 doc, 'custom_source_warehouse') and hasattr(
#                     doc, 'custom_reserved_qty'
#                 ) and doc.custom_source_warehouse and doc.custom_reserved_qty:
#             # Call your existing function
#             result = unreserve_on_row_delete(
#                 item_code=doc.item_code,
#                 custom_source_warehouse=doc.custom_source_warehouse,
#                 reserved_qty=doc.custom_reserved_qty)
#             # Log the action
#             frappe.logger().info(
#                 f"Unreserved {doc.custom_reserved_qty} of {doc.item_code} from {doc.custom_source_warehouse}"
#             )
#             frappe.logger().info(f"Result: {result}")
#     except Exception as e:
#         frappe.logger().error(f"Error in unreserve on delete: {str(e)}")

#     frappe.msgprint(
#         f"Unreserved {doc.custom_reserved_qty} of {doc.item_code} from {doc.custom_source_warehouse}"
#     )


@frappe.whitelist()
def unreserve_stems(item_code, warehouse, stems_to_unreserve):
    stems_to_unreserve = int(stems_to_unreserve)

    bin_data = frappe.get_value("Bin", {
        "item_code": item_code,
        "warehouse": warehouse
    }, ["actual_qty", "reserved_qty"],
                                as_dict=True)

    if not bin_data:
        return {
            "unreserved_qty": 0,
            "status": "Not Found",
            "message": f"No bin found for {item_code} in {warehouse}."
        }

    updated_reserved = max(0, bin_data.reserved_qty - stems_to_unreserve)

    frappe.db.set_value("Bin", {
        "item_code": item_code,
        "warehouse": warehouse
    }, "reserved_qty", updated_reserved)

    return {
        "unreserved_qty":
        stems_to_unreserve,
        "status":
        "Unreserved",
        "message":
        f"Unreserved {stems_to_unreserve} stems of {item_code} from {warehouse} back to Available for Sale."
    }
