import frappe
from frappe import _
from frappe.model.document import Document


class FarmPackList(Document):

    def on_update_after_submit(self):
        # Check if status is "Reviewed" and trigger stock transfer
        if self.custom_status == "Reviewed" and not frappe.db.exists(
                "Stock Entry", {
                    "farm_pack_list": self.name,
                    "stock_entry_type": "Material Transfer",
                    "docstatus": 1
                }):
            transfer_stock_on_review(self)
            # Also process consolidated pack list when reviewed
            process_consolidated_pack_list(self.name)

    def on_submit(self):
        # Keep original behavior for backward compatibility
        pass

    def on_cancel(self):
        transfer_stock_on_cancel(self)


@frappe.whitelist()
def transfer_stock_on_review(doc):
    """Transfers stock when Farm Pack List status is changed to Reviewed"""
    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    source_warehouses = [
        "Burguret Graded Sold - TL", "Pendekeza Graded Sold - TL",
        "Turaco Graded Sold - TL"
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
        f"✅ Stock Transfer: Items moved from {source_warehouse} to Delivery Truck successfully! The Farm Pack List is now ready for consolidation.",
        alert=True,
        indicator="green",
        wide=True,
    )


# Keeping original function for backward compatibility, but it won't be used in the workflow
@frappe.whitelist()
def transfer_stock_on_submit(doc):
    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    source_warehouses = [
        "Burguret Graded Sold - TL", "Pendekeza Graded Sold - TL",
        "Turaco Graded Sold - TL"
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


@frappe.whitelist()
def transfer_stock_on_cancel(doc):
    """Transfers stock from delivery truck back to original warehouse when Farm Pack List is cancelled."""

    if not doc.pack_list_item:
        frappe.throw("No items in Farm Pack List to transfer.")

    source_warehouse = "Delivery Truck - TL"  # Stock is moving FROM delivery truck

    dispatch_warehouses = [
        "Burguret Graded Sold - TL", "Pendekeza Graded Sold - TL",
        "Turaco Graded Sold - TL"
    ]

    # Get the original source warehouse from pack list item
    target_warehouse = None
    for item in doc.pack_list_item:
        if item.source_warehouse in dispatch_warehouses:
            target_warehouse = item.source_warehouse
            break

    if not target_warehouse:
        frappe.throw(
            f"Cannot determine original warehouse to return stock to. Please check the source warehouses in the Farm Pack List items."
        )

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
        f"❌ Stock Transfer: Items returned from Delivery Truck to {target_warehouse}. The Farm Pack List has been cancelled.",
        alert=True,
        indicator="red",
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

    # Fetch sales_order_id from the first Pack List Item if not provided
    if not sales_order_id and farm_pack_doc.pack_list_item:
        sales_order_id = farm_pack_doc.pack_list_item[0].sales_order_id

    if not sales_order_id:
        frappe.throw("Sales Order ID is required to process the CPL.")

    # Fetch all related Farm Pack Lists via Pack List Item
    related_farm_packs = frappe.get_all(
        "Pack List Item",
        filters={"sales_order_id": sales_order_id},
        fields=["parent"]  # 'parent' links to Farm Pack List
    )

    # Extract unique Farm Pack List IDs
    farm_pack_list_ids = list(
        set(pack["parent"] for pack in related_farm_packs))

    # Fetch total stems from related Farm Pack Lists
    related_farm_pack_docs = frappe.get_all(
        "Farm Pack List",
        filters={"name": ["in", farm_pack_list_ids]},
        fields=["custom_total_stems"])

    # Calculate the total stems
    total_stems = sum(fpl["custom_total_stems"]
                      for fpl in related_farm_pack_docs)

    # Check for an existing Consolidated Pack List (CPL)
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
            message = f"📋 Farm Pack List added to existing CPL: {cpl.name}"
        else:
            cpl = frappe.new_doc("Consolidated Pack List")
            cpl.sales_order_id = sales_order_id
            cpl.customer_id = farm_pack_doc.pack_list_item[0].customer_id
            message = "📋 New Consolidated Pack List created in draft status"

        # **Fetch required fields from Farm Pack List**
        cpl.custom_customer = farm_pack_doc.custom_customer
        cpl.custom_currency = farm_pack_doc.custom_currency
        cpl.custom_customer_address = farm_pack_doc.custom_customer_address
        cpl.custom_total_stems = total_stems

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
