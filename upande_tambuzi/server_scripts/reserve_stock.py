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
