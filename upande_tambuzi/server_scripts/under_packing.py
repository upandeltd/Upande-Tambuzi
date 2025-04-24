import frappe
from frappe import _
#from frappe.model.document import Document
from upande_tambuzi.upande_tambuzi.doctype.farm_pack_list.farm_pack_list import transfer_stock_on_submit, process_consolidated_pack_list


@frappe.whitelist()
def request_under_pack_authorization(doc_name):
    """Request authorization for under packed FPL"""
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to request under pack authorization"))

    doc = frappe.get_doc("Farm Pack List", doc_name)

    # Check if completion is less than 100%
    packed_stems = doc.custom_total_stems or 0
    required_stems = doc.custom_picked_total_stems or 0
    completion_percentage = 0

    if required_stems > 0:
        completion_percentage = (packed_stems / required_stems) * 100

    if completion_percentage >= 100:
        frappe.throw(_("This Farm Pack List is already fully packed"))

    # Check if reason is provided
    if not doc.custom_under_pack_reason:
        frappe.throw(_("Please provide a reason for under packing"))

    # Update workflow state to send for review
    doc.db_set('workflow_state', 'Pending Order Review', update_modified=True)

    return True


@frappe.whitelist()
def approve_under_pack(doc_name):
    """Approve under packed FPL by Sales Manager"""
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to approve under pack authorization"))

    if 'Sales Manager' not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Only Sales Managers can approve under packed FPLs"))

    doc = frappe.get_doc("Farm Pack List", doc_name)

    # Set workflow state to Reviewed
    doc.db_set('workflow_state', 'Reviewed', update_modified=True)

    # Add a comment for audit trail
    frappe.get_doc({
        "doctype":
        "Comment",
        "comment_type":
        "Info",
        "reference_doctype":
        "Farm Pack List",
        "reference_name":
        doc_name,
        "content":
        f"Under Pack approved by {frappe.session.user}. Reason: {doc.custom_under_pack_reason}"
    }).insert(ignore_permissions=True)

    # Trigger stock transfer and CPL update
    transfer_stock_on_submit(doc)
    process_consolidated_pack_list(doc.name)

    return True


@frappe.whitelist()
def reject_under_pack(doc_name):
    """Reject under packed FPL by Sales Manager"""
    if not frappe.has_permission("Farm Pack List", "write"):
        frappe.throw(_("Not permitted to reject under pack authorization"))

    # Check if user has Sales Manager role
    if 'Sales Manager' not in frappe.get_roles(frappe.session.user):
        frappe.throw(_("Only Sales Managers can approve under packed FPLs"))

    doc = frappe.get_doc("Farm Pack List", doc_name)

    doc.db_set('workflow_state', 'Rejected', update_modified=True)

    return True
