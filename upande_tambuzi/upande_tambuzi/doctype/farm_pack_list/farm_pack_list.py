import frappe
from frappe import _
from frappe.model.document import Document


class FarmPackList(Document):

    def on_submit(self):
        transfer_stock_on_submit(self)

    def on_cancel(self):
        transfer_stock_on_disable(self)


@frappe.whitelist()
def transfer_stock_on_submit(doc):

    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    source_warehouses = [
        "Burguret Dispatch Cold Store - TL",
        "Pendekeza Dispatch Cold Store - TL", "Turaco Dispatch Cold Store - TL"
    ]

    source_warehouse = None
    for item in doc.pack_list_item:
        if item.source_warehouse in source_warehouses:
            source_warehouse = item.source_warehouse
            break

    if not source_warehouse:
        frappe.throw(
            "Invalid or missing source warehouse. Allowed warehouses: " +
            ", ".join(source_warehouses))

    target_warehouse = "Delivery Truck - TL"

    if not frappe.db.exists("Warehouse", source_warehouse):
        frappe.throw(f"Source Warehouse '{source_warehouse}' does not exist.")

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.farm_pack_list = doc.name

    for item in doc.pack_list_item:
        stock_entry.append(
            "items", {
                "s_warehouse": source_warehouse,
                "t_warehouse": target_warehouse,
                "item_code": item.item_code,
                "qty": item.bunch_qty,
                "uom": item.bunch_uom,
                "stock_uom": item.bunch_uom,
            })

    stock_entry.save(ignore_permissions=True)
    stock_entry.submit()

    frappe.msgprint(
        f"Stock Transfer Created from {source_warehouse} to {target_warehouse} Successfully!",
        alert=True,
        indicator="green",
        wide=True,
    )


# stock transfer when farm pack list is disabled


@frappe.whitelist()
def transfer_stock_on_disable(doc):
    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    target_warehouses = [
        "Burguret Dispatch Cold Store - TL",
        "Pendekeza Dispatch Cold Store - TL", "Turaco Dispatch Cold Store - TL"
    ]

    target_warehouse = None
    for item in doc.pack_list_item:
        if item.source_warehouse in target_warehouses:
            target_warehouse = item.source_warehouse
            break

    if not target_warehouse:
        frappe.throw(
            "Invalid or missing target warehouse. Allowed warehouses: " +
            ", ".join(target_warehouses))

    source_warehouse = "Delivery Truck - TL"

    if not frappe.db.exists("Warehouse", target_warehouse):
        frappe.throw(f"Target Warehouse '{target_warehouse}' does not exist.")

    stock_entry = frappe.new_doc("Stock Entry")
    stock_entry.stock_entry_type = "Material Transfer"
    stock_entry.farm_pack_list = doc.name

    for item in doc.pack_list_item:
        stock_entry.append(
            "items", {
                "s_warehouse": source_warehouse,
                "t_warehouse": target_warehouse,
                "item_code": item.item_code,
                "qty": item.bunch_qty,
                "uom": item.bunch_uom,
                "stock_uom": item.bunch_uom,
            })

    stock_entry.save(ignore_permissions=True)
    stock_entry.submit()

    frappe.msgprint(
        f"Stock Transfer Created from {source_warehouse} to {target_warehouse} Successfully after cancellation of farm pack list!",
        alert=True,
        indicator="green",
        wide=True,
    )


@frappe.whitelist()
def process_consolidated_pack_list(farm_pack_list, sales_order_id=None):
    """Creates or updates Consolidated Pack List and triggers stock transfer"""
    if not frappe.has_permission("Farm Pack List", "read"):
        frappe.throw("Not permitted to read Farm Pack List")
    if not frappe.has_permission("Consolidated Pack List", "write"):
        frappe.throw("Not permitted to create/modify Consolidated Pack List")

    farm_pack_doc = frappe.get_doc("Farm Pack List", farm_pack_list)

    if not sales_order_id and farm_pack_doc.pack_list_item:
        sales_order_id = farm_pack_doc.pack_list_item[0].sales_order_id

    if not sales_order_id:
        frappe.throw("Sales Order ID is required to process the CPL.")

    existing_cpl = frappe.get_all("Consolidated Pack List",
                                  filters={"sales_order_id": sales_order_id},
                                  fields=["name"],
                                  limit=1)

    try:
        if existing_cpl:
            cpl = frappe.get_doc("Consolidated Pack List",
                                 existing_cpl[0]["name"])
            if not cpl.has_permission("write"):
                frappe.throw("Not permitted to modify this CPL")
            message = f"Farm Pack List updated CPL: {cpl.name}"
        else:
            cpl = frappe.new_doc("Consolidated Pack List")
            cpl.sales_order_id = sales_order_id
            cpl.customer_id = farm_pack_doc.pack_list_item[0].customer_id
            message = f"New CPL{cpl.name} is created in draft status"

        if "items" not in cpl.as_dict():
            frappe.throw("Field 'items' does not exist in CPL")

        for item in farm_pack_doc.pack_list_item:
            cpl.append(
                "items", {
                    "source_warehouse": "Delivery Truck - TL",
                    "customer_id": item.customer_id,
                    "sales_order_id": item.sales_order_id,
                    "box_id": item.box_id,
                    "item_code": item.item_code,
                    "bunch_uom": item.bunch_uom,
                    "bunch_qty": item.bunch_qty,
                    "stem_length": item.stem_length,
                    "consolidated_pack_list_id":
                    item.consolidated_pack_list_id,
                    "custom_number_of_stems": item.custom_number_of_stems
                })

        cpl.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.msgprint(
            message,
            alert=True,
            indicator="green",
            wide=True,
        )

        return cpl.name

    except Exception as e:
        frappe.db.rollback()
        frappe.throw(f"Error processing CPL: {str(e)}")


@frappe.whitelist()
def close_farm_pack_list(farm_pack_list):

    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to close Farm Pack List"))

    doc = frappe.get_doc("Farm Pack List", farm_pack_list)
    if doc.custom_status == "Closed":
        frappe.throw(_("Farm Pack List is already closed"))

    doc.db_set('custom_status', 'Closed', update_modified=False)
    doc.notify_update()
    frappe.db.commit()
    return True
