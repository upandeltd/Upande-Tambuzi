
import frappe

@frappe.whitelist()
def save_farm_pack_list(farm_pack_list_id, item_code, uom, quantity, source_warehouse, box_id):
    pack_list_doc = frappe.get_doc("Farm Pack List", farm_pack_list_id)

    pack_list_doc.append("pack_list_item", {
        "item_code": item_code,
        "uom": uom,
        "qty": quantity,
        "source_warehouse": source_warehouse,
        "box_id": box_id
    })

    pack_list_doc.save()

    return {"success": True, "message": "Farm Pack List updated successfully!"}
