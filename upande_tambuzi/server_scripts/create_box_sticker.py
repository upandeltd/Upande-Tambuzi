import frappe

import frappe.utils

@frappe.whitelist()
def create_box_sticker(variety, uom, customer, length, box_number, ):
    date = frappe.utils.today()

    boxStickerDoc = frappe.new_doc("Box Label")
    boxStickerDoc.customer = customer
    boxStickerDoc.length = length
    boxStickerDoc.box_number = box_number
    boxStickerDoc.date = date
    packrate = 0

    # For one bunch per scan
    quantity = 1

    boxStickerDoc.append("box_item", {
        "variety": variety,
        "qty": quantity,
        "uom": uom,
    })

    uom_conversion_factor = {
        "Bunch (5)": 5,
        "Bunch (6)": 6,
        "Bunch (10)": 10,
        "Bunch (12)": 12
    }

    packrate = uom_conversion_factor.get(uom, 0) * quantity

    boxStickerDoc.pack_rate = packrate

    boxStickerDoc.insert()

    return {
        "docname": boxStickerDoc.name
    }


