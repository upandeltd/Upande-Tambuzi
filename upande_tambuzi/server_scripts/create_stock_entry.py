import json
import frappe

@frappe.whitelist()
def create_stock_entry(stock_entry_data):
    stock_entry_data = json.loads(stock_entry_data)

    stock_entry = frappe.new_doc("Stock Entry")

    stock_entry_type = stock_entry_data.get("stock entry type")
    variety = stock_entry_data.get("variety")
    quantity = stock_entry_data.get("quantity")
    breeder = stock_entry_data.get("breeder")
    grower = stock_entry_data.get("grower")
    location_data = stock_entry_data.get("location data")
    uom = stock_entry_data.get("uom")
    
    stock_entry.stock_entry_type = stock_entry_type 

    stock_entry.append("items", {
        "item_code": variety,
        "qty": quantity,
        # Assumption is that the UOM of the scanned item (flower) is stem
        "custom_number_of_stems": quantity,
        "s_warehouse": location_data["source"],
        "t_warehouse": location_data["target"],
        "custom_breeder": breeder,
        "custom_grower": grower,
        "uom": uom
    })
    
    stock_entry.insert()
    
    # Submit the stock entry
    # stock_entry.submit()
    print(f'stock entry object: {stock_entry.name}')

    response_data = {
        "name": stock_entry.name
    }

    return json.dumps(response_data)
