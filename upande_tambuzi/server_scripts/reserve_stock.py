import frappe


@frappe.whitelist()
def reserve_stems(item_code, custom_source_warehouse, stems_requested,
                  sales_order_item):
    stems_requested = int(stems_requested)

    # Destination warehouse (Reserve)
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

        # Create stock entry
        if sales_order_item and not sales_order_item.startswith("new-"):
            # Cancel existing stock entries
            cancel_stock_entry_for_sales_order_item(sales_order_item)

            # Create new stock entry
            stock_entry_name = create_stock_entry(
                item_code=item_code,
                source_warehouse=custom_source_warehouse,
                target_warehouse=graded_reserve_warehouse,
                qty=stems_to_reserve,
                sales_order_item=sales_order_item)
            if stock_entry_name:
                frappe.msgprint(
                    f"Stock Entry {stock_entry_name} created for {item_code}")

    return {
        "reserved_qty":
        stems_to_reserve,
        "status":
        "Reserved" if stems_to_reserve > 0 else "Insufficient Stock",
        "message":
        f"{'Reserved' if stems_to_reserve > 0 else 'Could not reserve'} {stems_to_reserve} stems for {item_code}."
    }


def create_stock_entry(item_code, source_warehouse, target_warehouse, qty,
                       sales_order_item):
    if not frappe.db.exists("Sales Order Item", sales_order_item):
        return None
    try:
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.purpose = "Material Transfer"
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.from_warehouse = source_warehouse
        stock_entry.to_warehouse = target_warehouse
        stock_entry.custom_sales_order_item = sales_order_item
        stock_entry.append(
            "items", {
                "item_code":
                item_code,
                "qty":
                qty,
                "s_warehouse":
                source_warehouse,
                "t_warehouse":
                target_warehouse,
                "basic_rate":
                frappe.get_value("Item", item_code, "valuation_rate") or 0
            })
        stock_entry.insert()
        stock_entry.submit()
        frappe.db.commit()
        return stock_entry.name
    except Exception as e:
        frappe.log_error(f"Error creating stock entry: {str(e)}",
                         "Stock Entry Creation")
        return None


@frappe.whitelist()
def cancel_stock_entry_for_sales_order_item(sales_order_item):
    if not sales_order_item or sales_order_item.startswith("new-"):
        return 0

    stock_entries = frappe.get_all("Stock Entry",
                                   filters={
                                       "custom_sales_order_item":
                                       sales_order_item,
                                       "docstatus": 1
                                   },
                                   pluck="name")

    cancelled_count = 0
    for se_name in stock_entries:
        try:
            se = frappe.get_doc("Stock Entry", se_name)
            se.cancel()
            cancelled_count += 1
        except Exception as e:
            frappe.log_error(
                f"Failed to cancel Stock Entry {se_name}: {str(e)}")

    return cancelled_count


@frappe.whitelist()
def delete_reservation_and_stock_entry(sales_order_item):
    """Used when deleting a Sales Order Item"""
    if not sales_order_item or sales_order_item.startswith("new-"):
        return
    cancel_stock_entry_for_sales_order_item(sales_order_item)
    # TODO: Optionally unreserve stock here if you want


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
