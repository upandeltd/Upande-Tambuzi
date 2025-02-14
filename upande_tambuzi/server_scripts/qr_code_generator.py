import json
import qrcode
import frappe
import os
from PIL import Image, ImageDraw, ImageFont
import time

@frappe.whitelist(allow_guest=True)
def generate_qr_code(stock_entry_details):
    url = frappe.utils.get_url()

    stock_entry_details = json.loads(stock_entry_details)

    stock_entry_name = stock_entry_details['name']
    graded_by = stock_entry_details.get('grader')
    stock_entry_url = f"{url}/app/stock-entry/{stock_entry_name}"
    unique_id = int(time.time())

    bucket_details = {
        "Variety": stock_entry_details.get('variety'),
        "Stock Entry URL": stock_entry_url
    }

    variety = bucket_details.get("Variety", "Unknown Variety")

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(stock_entry_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')

    qr_width, qr_height = qr_img.size
    spacing = 10
    standard_width = 550

    label_font_size = int(standard_width * 0.08)

    try:
        font = ImageFont.truetype("arial.ttf", label_font_size)
    except IOError:
        font = ImageFont.load_default(label_font_size)

    variety_bbox = font.getbbox(variety)
    graded_by_bbox = font.getbbox(graded_by)

    label_width = max(variety_bbox[2] - variety_bbox[0], graded_by_bbox[2] - graded_by_bbox[0])
    
    variety_height = variety_bbox[3] - variety_bbox[1]
    stock_entry_height = graded_by_bbox[3] - graded_by_bbox[1]
    label_height = variety_height + stock_entry_height + spacing

    canvas_height = label_height + qr_height

    canvas = Image.new("RGB", (standard_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)

    variety_x = (standard_width - (variety_bbox[2] - variety_bbox[0])) // 2
    variety_y = 0
    draw.text((variety_x, variety_y), variety, font=font, fill="black")

    graded_by_x = (standard_width - (graded_by_bbox[2] - graded_by_bbox[0])) // 2
    graded_by_y = variety_height + spacing 
    draw.text((graded_by_x, graded_by_y), graded_by, font=font, fill="black")

    # Paste the QR code below the label
    qr_x = (standard_width - qr_width) // 2
    qr_y = label_height + spacing
    canvas.paste(qr_img, (qr_x, qr_y))

    qr_codes_dir_path = frappe.utils.get_files_path("qr_codes")
    os.makedirs(qr_codes_dir_path, exist_ok = True)
    
    file_path = os.path.join(qr_codes_dir_path, f"{stock_entry_name}_{unique_id}.png")
    canvas.save(file_path)

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_url": f"/files/qr_codes/{stock_entry_name}_{unique_id}.png",
        "attached_to_doctype": "Stock Entry",
        "attached_to_name": stock_entry_name,
        "is_private": 0
    })

    file_doc.insert()

    final_qr_code_url = file_doc.file_url

    return final_qr_code_url