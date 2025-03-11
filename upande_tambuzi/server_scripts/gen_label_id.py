import json
import os
import time
import frappe
import qrcode
import base64
from io import BytesIO

@frappe.whitelist()
def generate_id(no_of_labels, label_doc_name, action, variety=None,  farm=None, stem_length=None, bunch_size=None, grader=None):
    # Generate Bucket id
    # Encode the bucket id and variety in the qr code

    unique_id = int(time.time())
    
    qr_codes = []

    qr_codes_dir_path = frappe.utils.get_files_path("qr_codes")
    os.makedirs(qr_codes_dir_path, exist_ok=True)

    no_of_labels_int = int(no_of_labels)

    if action == "Harvesting Label":

        for i in range(1, no_of_labels_int + 1):
            bucket_id = f"BUCKET-{frappe.generate_hash(length=10)}-{i}"

            qr_data = {
                "item_code": variety,
                "bucket_id": bucket_id
            }

            qr_data_string = json.dumps(qr_data)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=4,
                border=2,
            )

            qr.add_data(qr_data_string)
            qr.make(fit=True)
            qr_img = qr.make_image(fill='black', back_color='white')

            file_name = f"{label_doc_name}_{unique_id}_{i}.png"
            file_path = os.path.join(qr_codes_dir_path, file_name)
            qr_img.save(file_path)

            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_url": f"/files/qr_codes/{file_name}",
                "attached_to_doctype": "Stock Entry",
                "attached_to_name": label_doc_name,
                "is_private": 0
            })

            file_doc.insert(ignore_permissions=True)


            qr_doc = frappe.get_doc({
                "doctype": "Bucket QR Code",
                "id": bucket_id,
                "item_code": variety,
                "qr_code_image": file_doc.file_url,
                "label_print_doc": label_doc_name
            })
            qr_doc.insert(ignore_permissions=True)
            frappe.db.commit()

    if action == "Bunch Label":
        for i in range(1, no_of_labels_int + 1):
            bunch_id = f'BUNCH-{frappe.generate_hash(length=10)}-{i}'

            qr_data = {
                "farm": farm,
                "variety": variety,
                "stem_length": stem_length,
                "bunch_size": bunch_size,
                "bunch_id": bunch_id
            }

            qr_data_string = json.dumps(qr_data)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=4,
                border=2,
            )

            qr.add_data(qr_data_string)
            qr.make(fit=True)
            qr_img = qr.make_image(fill='black', back_color='white')

            file_name = f"{label_doc_name}_{unique_id}_{i}.png"
            file_path = os.path.join(qr_codes_dir_path, file_name)
            qr_img.save(file_path)

            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_url": f"/files/qr_codes/{file_name}",
                "attached_to_doctype": "Stock Entry",
                "attached_to_name": label_doc_name,
                "is_private": 0
            })

            file_doc.insert(ignore_permissions=True)


            qr_doc = frappe.get_doc({
                "doctype": "Bunch QR Code",
                "id": bunch_id,
                "item_code": variety,
                "qr_code_image": file_doc.file_url,
                "label_print_doc": label_doc_name,
                "bunch_size": bunch_size,
                "stem_length": stem_length,
                "farm": farm

            })
            qr_doc.insert(ignore_permissions=True)
            frappe.db.commit()


    if action == "Grader Label":
        for i in range(1, no_of_labels_int + 1):
            bunch_id = f'GRADER-{frappe.generate_hash(length=10)}-{i}'

            qr_data = {
                "grader": grader,

            }

            qr_data_string = json.dumps(qr_data)

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=4,
                border=2,
            )

            qr.add_data(qr_data_string)
            qr.make(fit=True)
            qr_img = qr.make_image(fill='black', back_color='white')

            file_name = f"{label_doc_name}_{unique_id}_{i}.png"
            file_path = os.path.join(qr_codes_dir_path, file_name)
            qr_img.save(file_path)

            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_url": f"/files/qr_codes/{file_name}",
                "attached_to_doctype": "Stock Entry",
                "attached_to_name": label_doc_name,
                "is_private": 0
            })

            file_doc.insert(ignore_permissions=True)

            qr_doc = frappe.get_doc({
                "doctype": "Grader QR Code",
                "qr_code_image": file_doc.file_url,
                "label_print_doc": label_doc_name,
                "grader": grader,

            })
            qr_doc.insert(ignore_permissions=True)
            frappe.db.commit()

    frappe.response["message"] = f"Label created Successfully"

