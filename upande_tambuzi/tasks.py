import frappe
from frappe.utils import now_datetime, add_days

@frappe.whitelist()
def transfer_stock():
    last_24_hours = add_days(now_datetime(), -1)
    
    stock_entries = frappe.get_all(
        "Stock Entry",
        filters={
            "stock_entry_type": ["in", ["Grading", "Grading without Receiving"]],
            "creation": [">=", last_24_hours]
        },
        fields=["name", "stock_entry_type"]
    )
    
    if not stock_entries:
        frappe.log_error("✅ No eligible stock entries found for transfer.")
        return
    
    for entry in stock_entries:
        try:
            stock_entry = frappe.get_doc("Stock Entry", entry["name"])
            farm_name = stock_entry.custom_farm
            
            from_warehouse = f"{farm_name} Graded General - TL"
            to_warehouse = f"{farm_name} Available for Sale - TL"
            
            new_stock_entry = frappe.new_doc("Stock Entry")
            new_stock_entry.stock_entry_type = "Material Transfer"
            
            new_stock_entry.from_warehouse = from_warehouse
            new_stock_entry.to_warehouse = to_warehouse
            
            for item in stock_entry.items:
                new_stock_entry.append("items", {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "s_warehouse": from_warehouse,
                    "t_warehouse": to_warehouse
                })
                
            print(f'{to_warehouse}')
            new_stock_entry.save()
            new_stock_entry.submit()
            frappe.db.commit()
            print(f"Submitted Stock Entry {new_stock_entry.name}")
            
        except Exception as e:
            frappe.log_error(f"❌ Error processing Stock Entry {entry['name']}: {str(e)}")
    