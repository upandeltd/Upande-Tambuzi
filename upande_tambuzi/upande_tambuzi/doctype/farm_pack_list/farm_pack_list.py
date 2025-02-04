import frappe
from frappe.model.document import Document

class FarmPackList(Document):
    pass

@frappe.whitelist()
def create_consolidated_pack_list(farm_pack_list):
    farm_doc = frappe.get_doc("Farm Pack List", farm_pack_list)
    
    consolidated_list = frappe.new_doc("Consolidated Pack List")
    
    # Add items from farm pack list
    for item in farm_doc.pack_list_item:  
        consolidated_list.append('items', {
            'sales_order_id': item.sales_order_id,
            'item_group': frappe.get_value('Item', item.item_code, 'item_group'),
            'item_code': item.item_code,
            'source_warehouse': item.source_warehouse,
            'box_id': item.box_id,
            'customer_id':item.customer_id,
            'length': item.length if hasattr(item, 'length') else None,
            'bunched_by': item.uom,
            'bunches': item.qty,
            #'stems': item.qty * get_stems_per_bunch(item.uom),
            'packing_list': farm_pack_list
        })
    
    consolidated_list.insert()
    frappe.db.commit()
    return consolidated_list.name

def get_stems_per_bunch(uom):
    # Extract the number from UOM like "Bunch(5)" -> returns 5
    import re
    match = re.search(r'\((\d+)\)', uom)
    return int(match.group(1)) if match else 1