import frappe
from frappe.utils import nowdate
from collections import defaultdict

@frappe.whitelist()
def create_pick_list_for_sales_order(doc, method=None):
    # Handle both document object and document name
    if isinstance(doc, str):
        sales_order = frappe.get_doc("Sales Order", doc)
    else:
        sales_order = doc

    if not sales_order:
        frappe.throw("Sales Order is required to create Pick Lists.")

    # Check if Pick Lists already exist for this Sales Order
    existing_pick_lists = frappe.get_all(
        "Pick List",
        filters={
            "sales_order": sales_order.name,
            "docstatus": ["!=", 2]  # Not cancelled
        }
    )
    
    if existing_pick_lists:
        frappe.throw(f"Pick Lists already exist for Sales Order {sales_order.name}")

    # Ensure the Sales Order is submitted
    if sales_order.docstatus != 1:
        frappe.throw("Pick List can only be created for submitted Sales Orders.")

    # Group items by custom_source_warehouse
    warehouse_groups = defaultdict(list)

    # Fetch all necessary fields from Sales Order Items
    sales_order_items = frappe.get_all(
        "Sales Order Item",
        filters={"parent": sales_order.name},
        fields=[
            "item_code",
            "item_name",
            "stock_uom",
            "uom",
            "qty",
            "custom_source_warehouse",
            "conversion_factor",
            "stock_qty",
            "against_blanket_order"
        ]
    )
# Validate and group items
    for item in sales_order_items:
        if not item.source_warehouse:
            frappe.throw(f"Source warehouse not specified for item {item.item_code}")
            
        if not item.qty or item.qty <= 0:
            frappe.throw(f"Item {item.item_code} has invalid quantity: {item.qty}")
            
        warehouse_groups[item.source_warehouse].append(item)

    if not warehouse_groups:
        frappe.throw("No valid items found in Sales Order for creating Pick Lists")

    # Create separate Pick Lists for each source warehouse
    pick_list_names = []
    
    try:
        for warehouse, items in warehouse_groups.items():
            pick_list = frappe.new_doc("Pick List")
            pick_list.purpose = "Delivery"
            pick_list.sales_order = sales_order.name
            pick_list.company = sales_order.company
            pick_list.customer = sales_order.customer
            pick_list.posting_date = nowdate()
            
            # Calculate total quantity for this warehouse
            total_stock_qty = sales_order.total_qty
            pick_list.for_qty = total_stock_qty

            # Add items to locations
            for item in items:
                location = pick_list.append("locations", {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "stock_uom": item.stock_uom,
                    "uom": item.uom,
                    "qty": item.qty,
                    "stock_qty": item.stock_qty,
                    "conversion_factor": item.conversion_factor,
                    "warehouse": item.warehouse,
                    "sales_order": sales_order.name,
                    "sales_order_item": item.name
                })

                # If item is against blanket order, set the reference
                if item.against_blanket_order:
                    location.against_pick_list = item.against_blanket_order

            pick_list.flags.ignore_permissions = True
            
            # Save and submit with error handling
            try:
                pick_list.save()
                pick_list.submit()
                pick_list_names.append(pick_list.name)
            except Exception as e:
                frappe.log_error(f"Failed to create Pick List for warehouse {warehouse}: {str(e)}")
                raise

    except Exception as e:
        frappe.log_error(f"Error creating Pick Lists for Sales Order {sales_order.name}: {str(e)}")
        raise

    if pick_list_names:
        frappe.msgprint(
            msg=f"Created Pick Lists for Sales Order {sales_order.name}: {', '.join(pick_list_names)}",
            title="Pick Lists Created",
            indicator="green"
        )
        
    return pick_list_names
