import frappe

@frappe.whitelist()
def add_bunch_to_farm_pack_list(farm_pack_list_doc_id, bunch_SE_name, opl_name, farm, box_id):
    try:
        order_id = opl_name

        stock_entry_id = bunch_SE_name
        
        order_pick_list = frappe.get_doc("Order Pick List", order_id)
        stock_entry = frappe.get_doc("Stock Entry", stock_entry_id)

        source_warehouse = f"{farm} Dispatch Cold Store - TL"
        item_code = stock_entry.items[0].item_code
        uom = stock_entry.items[0].uom

        # Quantity scanned should always be 1
        quantity = 1
        customer_id = order_pick_list.customer
        sales_order_id = order_pick_list.sales_order

        if farm_pack_list_doc_id:
            pack_list_doc = frappe.get_doc("Farm Pack List", farm_pack_list_doc_id)
        else:
            pack_list_doc = frappe.new_doc("Farm Pack List")
            pack_list_doc.farm = farm 

        pack_list_doc.append("pack_list_item", {
            "item_code": item_code,
            "uom": uom,
            "qty": quantity,
            "source_warehouse": source_warehouse,
            "sales_order_id": sales_order_id,
            "customer_id": customer_id,
            "box_id": box_id,
        })

        pack_list_doc.save()

        return {
            "message": f"Bunch successfully added to Farm Pack List: {pack_list_doc.name}",
            "docname": pack_list_doc.name
        }  
        
        

    except Exception as e:
        frappe.throw(f"Error adding bunch to Farm Pack List: {e}")
