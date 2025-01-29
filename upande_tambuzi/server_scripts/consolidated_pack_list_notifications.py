import frappe
from frappe.utils import get_datetime, now_datetime, add_minutes

def schedule_cpl_notifications(doc, method):
    """
    Schedules notifications for CPL approval.
    - Notifies Sales Manager after 30 minutes.
    - Notifies CEO after 60 minutes if still pending.
    """
    if doc.workflow_state == "Pending Approval":
        # Schedule Sales Manager notification after 30 minutes
        notify_time_sm = add_minutes(doc.creation, 30)
        frappe.enqueue(send_cpl_notification, queue='long', job_name=f"notify_sales_manager_{doc.name}",
                       doc_name=doc.name, role="Sales Manager", execute_at=notify_time_sm)

        # Schedule CEO notification after 60 minutes if still pending
        notify_time_ceo = add_minutes(doc.creation, 60)
        frappe.enqueue(send_cpl_notification, queue='long', job_name=f"notify_ceo_{doc.name}",
                       doc_name=doc.name, role="CEO", execute_at=notify_time_ceo)

def send_cpl_notification(doc_name, role):
    """Sends email and system notifications to the specified role."""
    doc = frappe.get_doc("Consolidated Pack List", doc_name)
    
    if doc.workflow_state != "Pending Approval":
        return  # Stop if CPL is already approved
    
    recipients = [user.name for user in frappe.get_all("User", filters={"role_profile_name": role}, fields=["name"])]
    
    if recipients:
        # Send system notification
        subject = f"Approval Required: Consolidated Pack List {doc.name}"
        message = f"The Consolidated Pack List {doc.name} is still pending approval. Please review and approve."
        for recipient in recipients:
            frappe.sendmail(recipients=recipient, subject=subject, message=message)
            
            # System notification
            frappe.get_doc({
                "doctype": "Notification Log",
                "subject": subject,
                "email_content": message,
                "for_user": recipient
            }).insert(ignore_permissions=True)

        frappe.db.commit()