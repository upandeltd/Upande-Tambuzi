# import frappe

# def update_cpl_progress(doc, method):
#     """Updates CPL progress based on submitted FPLs"""
#     if doc.sales_order:
#         # Get total expected FPLs (same as Pick Lists count for SO)
#         total_fpls = frappe.db.count("Pick List",
#                                      {"sales_order": doc.sales_order})

#         # Count submitted FPLs
#         submitted_fpls = frappe.db.count("Farm Pack List", {
#             "sales_order": doc.sales_order,
#             "docstatus": 1
#         })

#         # Calculate completion percentage
#         completion_percentage = (submitted_fpls /
#                                  total_fpls) * 100 if total_fpls else 0

#         # Update CPL
#         doc.completion_percentage = completion_percentage
#         doc.save()

#         # Prevent Approval if Not 100%
#         if completion_percentage < 100:
#             frappe.throw(
#                 "Cannot approve CPL until all Farm Pack Lists are submitted!")
