import frappe

# def auto_create_pick_list_on_sales_order_submit(doc, method):
#     try:
#         # Create a new Pick List document
#         pick_list = frappe.new_doc("Pick List")
        
#         # Set fields in the Pick List
#         pick_list.sales_order = doc.name
#         pick_list.purpose = "Delivery"  # Set the purpose explicitly if required
#         pick_list.qty_of_finished_goods_item = len(doc.items)  # Number of items in the Sales Order
        
#         # Append items to the 'locations' child table
#         for item in doc.items:
#             if item.qty > 0:  # Only include items with a quantity greater than zero
#                 pick_list.append("locations", {
#                     "item_code": item.item_code,
#                     "qty": item.qty,
#                     "warehouse": item.warehouse
#                 })
        
#         # Insert and submit the Pick List document
#         pick_list.insert()
#         pick_list.submit()
        
#         frappe.msgprint(f"Pick List {pick_list.name} created successfully for Sales Order {doc.name}.")
#     except Exception as e:
#         # Log the error for debugging
#         frappe.log_error(frappe.get_traceback(), "Auto Pick List Creation Error")
#         frappe.throw(f"An error occurred while creating the Pick List: {str(e)}")


def auto_create_pick_list_on_sales_order_submit(doc, method):
    try:
        if not doc.items:
            frappe.msgprint("No items found in Sales Order")
            return

        # Group items by warehouse using a dictionary of lists
        warehouse_items = {}
        
        # Debug log for initial items
        frappe.log_error("Initial Items:")
        for item in doc.items:
            frappe.log_error(f"Processing item {item.item_code} from warehouse {item.warehouse}")
            
            if not item.warehouse:
                continue
                
            if item.warehouse not in warehouse_items:
                warehouse_items[item.warehouse] = []
            
            warehouse_items[item.warehouse].append(item)

        frappe.log_error(f"Warehouse groups created: {list(warehouse_items.keys())}")
        
        if not warehouse_items:
            frappe.throw("No valid warehouse items found")

        created_pick_lists = []

        # Create separate pick list for each warehouse
        for warehouse, items in warehouse_items.items():
            frappe.log_error(f"Creating pick list for warehouse: {warehouse}")
            
            if not items:
                continue

            # Create new pick list
            pick_list = frappe.new_doc("Pick List")
            pick_list.purpose = "Delivery"
            pick_list.company = doc.company
            pick_list.customer = doc.customer
            pick_list.sales_order = doc.name

            # Add items for this specific warehouse
            for item in items:
                pick_list.append('locations', {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "stock_qty": item.stock_qty,
                    "uom": item.uom,
                    "stock_uom": item.stock_uom,
                    "sales_order": doc.name,
                    "sales_order_item": item.name,
                    "warehouse": warehouse,
                    "batch_no": item.get("batch_no")
                })

            # Save and submit the pick list
            pick_list.insert()
            pick_list.submit()
            created_pick_lists.append(pick_list.name)
            frappe.log_error(f"Created Pick List {pick_list.name} for warehouse {warehouse}")

        # Show success message
        if created_pick_lists:
            message = "Created Pick Lists:\n"
            for pick_list_name in created_pick_lists:
                message += f"• {pick_list_name} \n"
            frappe.msgprint(msg=message, title="Pick Lists Created")
        
    except Exception as e:
        frappe.log_error(f"Error in pick list creation: {str(e)}")
        frappe.throw(f"Failed to create pick lists: {str(e)}")