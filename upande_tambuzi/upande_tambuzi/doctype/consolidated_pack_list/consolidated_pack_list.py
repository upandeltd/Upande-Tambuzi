# Path: upande_tambuzi/upande_tambuzi/doctype/consolidated_pack_list/consolidated_pack_list.py

import frappe
from frappe import _
from frappe.model.document import Document

class ConsolidatedPackList(Document):

	pass
    # def on_submit(self):
    #     """
    #     Create Dispatch Form when Consolidated Pack List (CPL) is submitted
    #     """
    #     try:
    #         # Get items and ensure we have data
    #         items = self.get('items', [])
    #         if not items:
    #             frappe.throw(_("No items found in the Consolidated Pack List"))
            
    #         # Group box counts by Customer ID and Item Code
    #         box_counts = {}
    #         for item in items:
    #             if not item.customer_id or not item.item_code:
    #                 frappe.throw(_("Customer ID and Item Code are required for all items"))
                
    #             key = (item.customer_id, item.item_code)
    #             if key in box_counts:
    #                 box_counts[key]['boxes'] += 1
    #             else:
    #                 box_counts[key] = {
    #                     'customer_id': item.customer_id,
    #                     'item_code': item.item_code,
    #                     'boxes': 1
    #                 }
            
    #         if not box_counts:
    #             frappe.throw(_("No valid items found to create Dispatch Form"))
            
    #         # Create Dispatch Form
    #         dispatch_form = frappe.get_doc({
    #             "doctype": "Dispatch Form",
    #             "dispatch_form_item": [
    #                 {
    #                     "custom_consolidated_pack_list_id": self.name,
    #                     "custom_shipmentcustomer": data['customer_id'],
    #                     "custom_crop": data['item_group'],
    #                     "custom_no_of_boxes": data['boxes']
    #                 }
    #                 for key, data in box_counts.items()
    #             ]
    #         })
            
    #         # Debug log to check dispatch form data
    #         frappe.log_error(
    #             title="Dispatch Form Debug",
    #             message=f"Dispatch Form Data: {dispatch_form.as_dict()}"
    #         )
            
    #         # Save the dispatch form in draft mode
    #         dispatch_form.insert()
            
    #         frappe.msgprint(
    #             msg=_("Dispatch Form {0} has been created successfully").format(
    #                 dispatch_form.name
    #             ),
    #             title=_("Success")
    #         )
            
    #     except Exception as e:
    #         frappe.log_error(
    #             title="CPL to Dispatch Form Creation Error",
    #             message=f"Error while creating Dispatch Form from CPL {self.name}: {str(e)}\nFull traceback: {frappe.get_traceback()}"
    #         )
    #         frappe.throw(
    #             _("Error creating Dispatch Form. Please check the error log for details.")
    #         )