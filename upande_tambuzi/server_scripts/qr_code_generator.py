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

    stock_entry_name = stock_entry_details.get('name')
    graded_by_id = stock_entry_details.get('grader')
    stock_entry_url = f"{url}/app/stock-entry/{stock_entry_name}"
    unique_id = int(time.time())

    graded_by_name = frappe.db.get_value("Employee", graded_by_id, "employee_name") or "Unknown"

    bucket_details = {
        "Variety": stock_entry_details.get('variety'),
        "Stock Entry URL": stock_entry_url
    }

    # Should generate the number of qr codes equal to the quantity value
    # The difference between the qr codes should just be numbering but have the 
    # url of the stock entry
    quantity = stock_entry_details.get('qty', 1)
    variety = bucket_details.get("Variety", "Unknown Variety")

    qr_codes_dir_path = frappe.utils.get_files_path("qr_codes")
    os.makedirs(qr_codes_dir_path, exist_ok = True)

    qr_codes = []



    for i in range(1, quantity + 1):
        bunch_id = f"{stock_entry_name}-Bunch-{i}"

        qr_data = {
            "url": stock_entry_url,
            "bunch_id": bunch_id
        }

        qr_data_string = ";".join([f"{key}={value}" for key, value in qr_data.items()])

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=4,
        )

        qr.add_data(qr_data_string)
        qr.make(fit=True)
        qr_img = qr.make_image(fill='black', back_color='white')

        qr_width, qr_height = qr_img.size
        spacing = 10
        standard_width = 550
        max_text_width = 500 

        initial_font_size = int(standard_width * 0.07)

        def fit_text(draw, text, max_width, font_path="arial.ttf", min_font_size=14):
            """ Adjust font size so text fits within max_width """
            font_size = initial_font_size
            while font_size > min_font_size:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                except IOError:
                    font = ImageFont.load_default()

                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]

                if text_width <= max_width:
                    return font, text_width, bbox[3] - bbox[1]
                font_size -= 2  # Reduce font size if too wide


        temp_canvas = Image.new("RGB", (1, 1), "white")
        temp_draw = ImageDraw.Draw(temp_canvas)

        variety_font, variety_width, variety_height = fit_text(temp_draw, variety, max_text_width)
        graded_by_text = f"Bunched by: {graded_by_name}"
        graded_by_font, graded_by_width, graded_by_height = fit_text(temp_draw, graded_by_text, max_text_width)

        label_height = variety_height + graded_by_height + spacing
        canvas_height = label_height + qr_height


        canvas = Image.new("RGB", (standard_width, canvas_height), "white")
        draw = ImageDraw.Draw(canvas)

        variety_x = (standard_width - variety_width) // 2
        variety_y = 0
        draw.text((variety_x, variety_y), variety, font=variety_font, fill="black")

        graded_by_x = (standard_width - graded_by_width) // 2
        graded_by_y = variety_height + spacing 
        draw.text((graded_by_x, graded_by_y), graded_by_text, font=graded_by_font, fill="black")

        # Paste the QR code below the label
        qr_x = (standard_width - qr_width) // 2
        qr_y = label_height + spacing
        canvas.paste(qr_img, (qr_x, qr_y))


        file_path = os.path.join(qr_codes_dir_path, f"{stock_entry_name}_{unique_id}_{i}.png")
        canvas.save(file_path)

        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_url": f"/files/qr_codes/{stock_entry_name}_{unique_id}_{i}.png",
            "attached_to_doctype": "Stock Entry",
            "attached_to_name": stock_entry_name,
            "is_private": 0
        })

        file_doc.insert(ignore_permissions=True)

        qr_code_doc = frappe.get_doc({
            "doctype": "QR Code",
            "bunch_id": bunch_id,
            "qr_code_image": file_doc.file_url,
            "stock_entry": stock_entry_name 
        })

        qr_code_doc.insert(ignore_permissions=True)
        frappe.db.commit() 

        qr_codes.append({
            "bunch_id": bunch_id,
            "qr_url": file_doc.file_url, 
            "qr_doctype_id": qr_code_doc.name  
        })

    return {"message": qr_codes}