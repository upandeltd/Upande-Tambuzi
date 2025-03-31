import frappe

@frappe.whitelist()
def add_bunch_to_farm_pack_list(farm_pack_list_doc_id, bunch_details, opl_name, farm, box_id):
    try:
        order_id = opl_name

        if isinstance(bunch_details, str):
            try:
                bunch_details = frappe.parse_json(bunch_details)
            except Exception as e:
                frappe.throw(f"Failed to parse bunch_details as JSON: {e}")

        order_pick_list = frappe.get_doc("Order Pick List", order_id)

        source_warehouse = f"{farm} Dispatch Cold Store - TL"

        # Check if this item already exists and bunch size matches on the fpl
        # If exists and matches the preexisting uom, increment 
        item_code = bunch_details.get("variety")
        uom = bunch_details.get("uom")
        stem_length = bunch_details.get("stem_length")

        # Quantity scanned should always be 1
        quantity = bunch_details.get("qty")
        customer_id = order_pick_list.customer
        sales_order_id = order_pick_list.sales_order

        stem_from_bunch = {
            "Bunch (5)": 5,
            "Bunch (6)": 6,
            "Bunch (10)": 10,
            "Bunch (12)": 12,
            "Bunch (25)": 25
        } 
        
        # add this to the existing number of stems
        bunch_stems = stem_from_bunch[uom]

        if farm_pack_list_doc_id:
            pack_list_doc = frappe.get_doc("Farm Pack List", farm_pack_list_doc_id)
        else:
            pack_list_doc = frappe.new_doc("Farm Pack List")
            pack_list_doc.farm = farm 

        # Track whether a match was found
        item_found = False

        for item in pack_list_doc.pack_list_item:
            if item.item_code == item_code and item.bunch_uom == uom:
                item.bunch_qty += 1
                item.custom_number_of_stems += bunch_stems

                item_found = True
                break  

        # If no matching item was found, add a new one
        if not item_found:
            pack_list_doc.append("pack_list_item", {
                "item_code": item_code,
                "bunch_uom": uom,
                "bunch_qty": quantity,
                "source_warehouse": source_warehouse,
                "sales_order_id": sales_order_id,
                "customer_id": customer_id,
                "box_id": box_id,
                "custom_number_of_stems": bunch_stems,
                "stem_length": stem_length
            })
        

        pack_list_doc.save()

        return {
            "message": f"Bunch successfully added to Farm Pack List: {pack_list_doc.name}",
            "docname": pack_list_doc.name
        }  
        
        

    except Exception as e:
        frappe.throw(f"Error adding bunch to Farm Pack List: {e}")
