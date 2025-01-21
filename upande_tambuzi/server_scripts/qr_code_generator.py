import qrcode
import frappe
import os

@frappe.whitelist()
def generate_qr_code_with_bucket_details(stock_entry_details):
    # url = frappe.utils.get_url()

    # stock_entry_url = f"{url}/app/stock-entry/{stock_entry_name}"

    stock_entry_name = stock_entry_details['name']

    bucket_details = {
        "Source Greenhouse": stock_entry_details.get('source_greenhouse'),
        "Variety": stock_entry_details.get('variety'),
        "Number of Stems": stock_entry_details.get('number_of_stems'),
    }

    bucket_details_text = "\n".join([f"{key}: {value}" for key, value in bucket_details.items()])
     
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(bucket_details_text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    qr_codes_dir_path = frappe.utils.get_files_path("qr_codes")
    os.makedirs(qr_codes_dir_path, exist_ok = True)
    
    file_path = os.path.join(qr_codes_dir_path, f"{stock_entry_name}.png")
    img.save(file_path)

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_url": f"/files/qr_codes/{stock_entry_name}.png",
        "attached_to_doctype": "Stock Entry",
        "attached_to_name": stock_entry_name,
        "is_private": 0
    })

    file_doc.insert()

    final_qr_code_url = f"{file_doc.file_url}"

    return final_qr_code_url