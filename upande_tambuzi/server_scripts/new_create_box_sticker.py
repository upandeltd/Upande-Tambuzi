import frappe

import frappe.utils

@frappe.whitelist()
def create_box_sticker(variety, uom, customer, length, box_number, customer_purchase_order, order_pick_list, quantity, scan_doc_id):
    date = frappe.utils.today()

    boxStickerDoc = frappe.new_doc("Box Label")
    scan_doc = frappe.get_doc("Scan", scan_doc_id)

    boxStickerDoc.customer = customer
    boxStickerDoc.length = length
    boxStickerDoc.box_number = box_number
    boxStickerDoc.date = date
    boxStickerDoc.customer_purchase_order = customer_purchase_order
    boxStickerDoc.order_pick_list = order_pick_list
    packrate = 0

    boxStickerDoc.append("box_item", {
        "variety": variety,
        "qty": quantity,
        "uom": uom,
    })


    scan_doc.append("scanned_items", {
        "variety": variety,
        "bunch_size": uom,
        "number_of_bunches": quantity
    })


    uom_conversion_factor = {
        "Bunch (5)": 5,
        "Bunch (6)": 6,
        "Bunch (10)": 10,
        "Bunch (12)": 12,
        "Bunch (25)": 25
    }

    packrate = uom_conversion_factor.get(uom) * int(quantity)

    boxStickerDoc.pack_rate = packrate

    boxStickerDoc.insert()

    return {
        "docname": boxStickerDoc.name
    }


