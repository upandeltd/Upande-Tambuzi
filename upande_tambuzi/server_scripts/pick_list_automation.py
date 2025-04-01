import frappe
from frappe.utils import nowdate
from collections import defaultdict

from upande_tambuzi.server_scripts.opl_qr_code_gen import generate_qr_code


@frappe.whitelist()
def create_pick_list_for_sales_order(doc, method=None):
    # Handle both document object and document name
    if isinstance(doc, str):
        sales_order = frappe.get_doc("Sales Order", doc)
    else:
        sales_order = doc

    if not sales_order:
        frappe.throw("Sales Order is required to create Order Pick Lists.")

    # Check if Pick Lists already exist for this Sales Order
    existing_order_pick_lists = frappe.get_all(
        "Order Pick List",
        filters={
            "sales_order": sales_order.name,
            "docstatus": ["!=", 2]  # Not cancelled
        })

    if existing_order_pick_lists:
        frappe.throw(
            f"Order Pick Lists already exist for Sales Order {sales_order.name}"
        )

    # Ensure the Sales Order is submitted
    if sales_order.docstatus != 1:
        frappe.throw(
            "An Order Pick List can only be created for submitted Sales Orders."
        )

    # Group items by custom_source_warehouse
    warehouse_groups = defaultdict(list)

    # Fetch all necessary fields from Sales Order Items
    sales_order_items = frappe.get_all(
        "Sales Order Item",
        filters={"parent": sales_order.name},
        fields=[
            "item_code", "item_name", "stock_uom", "uom", "qty",
            "custom_source_warehouse", "conversion_factor", "stock_qty",
            "custom_length", "against_blanket_order", "custom_box_id",
            "custom_box_label"
        ])
    # Validate and group items
    for item in sales_order_items:
        if not item.custom_source_warehouse:
            frappe.throw(
                f"Source warehouse not specified for item {item.item_code}")

        if not item.qty or item.qty <= 0:
            frappe.throw(
                f"Item {item.item_code} has invalid quantity: {item.qty}")

        warehouse_groups[item.custom_source_warehouse].append(item)

    if not warehouse_groups:
        frappe.throw(
            "No valid items found in Sales Order for creating Order Pick Lists"
        )

    # Create separate Pick Lists for each source warehouse
    order_pick_list_names = []

    try:
        for warehouse, items in warehouse_groups.items():
            order_pick_list = frappe.new_doc("Order Pick List")
            order_pick_list.purpose = "Delivery"
            order_pick_list.sales_order = sales_order.name
            order_pick_list.customer = sales_order.customer
            order_pick_list.date_created = nowdate()

            # Calculate total quantity for this warehouse
            total_stock_qty = sales_order.total_qty
            order_pick_list.for_qty = total_stock_qty

            # Add items to locations
            for item in items:
                location = order_pick_list.append(
                    "locations",
                    {
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "stock_uom": item.stock_uom,
                        "uom": item.uom,
                        "qty": item.qty,
                        "length": item.length,
                        "stock_qty": item.stock_qty,
                        "conversion_factor": item.conversion_factor,
                        "warehouse": item.
                        custom_source_warehouse,  # This pulls from Sales Order Item's source warehouse
                        "sales_order": sales_order.name,
                        "sales_order_item": item.name,
                        "custom_consignee": item.custom_consignee,
                        "custom_truck_details": item.custom_truck_details,
                        "custom_box_id": item.custom_box_id,
                        "custom_box_label": item.custom_box_label
                    })

                # If item is against blanket order, set the reference
                if item.against_blanket_order:
                    location.against_order_pick_list = item.against_blanket_order

                print(item.custom_source_warehouse, item.qty)

            order_pick_list.flags.ignore_permissions = True

            # Save and submit with error handling
            try:
                order_pick_list.save()

                # Generate and attach qrcode encoded with url of OPL
                opl_url = f"{frappe.utils.get_url()}/app/order-pick-list/{order_pick_list.name}"
                qr_code_url = generate_qr_code(opl_url, order_pick_list.name)

                order_pick_list = frappe.get_doc("Order Pick List",
                                                 order_pick_list.name)
                order_pick_list.custom_qr_code = qr_code_url

                #order_pick_list.save()

                #order_pick_list.submit()
                order_pick_list_names.append(order_pick_list.name)

                #order_pick_list.save()
            except Exception as e:
                frappe.log_error(
                    f"Failed to create Order Pick List for warehouse {warehouse}: {str(e)}"
                )
                raise

    except Exception as e:
        frappe.log_error(
            f"Error creating Order Pick Lists for Sales Order {sales_order.name}: {str(e)}"
        )
        raise

    if order_pick_list_names:
        frappe.msgprint(
            msg=
            f"Created Pick Lists for Sales Order {sales_order.name}: {', '.join(order_pick_list_names)}",
            title="Pick Lists Created",
            indicator="green")

    return order_pick_list_names
