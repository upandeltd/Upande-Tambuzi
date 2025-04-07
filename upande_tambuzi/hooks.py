app_name = "upande_tambuzi"
app_title = "Upande Tambuzi"
app_publisher = "Upande Limited"
app_description = "ERPNext project for Tambuzi Ltd, a dealer in flower operations."
app_email = "newton@upande.com"
app_license = "mit"

# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/upande_tambuzi/css/upande_tambuzi.css"
# app_include_js = "/assets/upande_tambuzi/js/upande_tambuzi.js"

# As a list to make sure it does not override_class
app_include_js = [
    "/assets/upande_tambuzi/client_scripts/fetch_item_grp_price.js",
    "/assets/upande_tambuzi/client_scripts/update_stock_sales_inv.js",
    "/assets/upande_tambuzi/client_scripts/se_rejection_reason.js",
    "/assets/upande_tambuzi/client_scripts/so_stock_transfer.js",
    "/assets/upande_tambuzi/client_scripts/autofetch_pricelist.js"
]

# include js, css files in header of web template
# web_include_css = "/assets/upande_tambuzi/css/upande_tambuzi.css"
# web_include_js = "/assets/upande_tambuzi/js/upande_tambuzi.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "upande_tambuzi/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}
# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "upande_tambuzi/public/login/tambuzi_logo.svg"

# Home Pages
# ----------

# add_to_apps_screen = [
#     {
#         "name": app_name,
#         "logo": "/assets/upande_tambuzi/Login/tambuzi_logo.ico",
#         "title": app_title,
#         "route": app_home,
#         "has_permission": "erpnext.check_app_permission",
#     }
# ]

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#   "Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#   "methods": "upande_tambuzi.utils.jinja_methods",
#   "filters": "upande_tambuzi.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "upande_tambuzi.install.before_install"
# after_install = "upande_tambuzi.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "upande_tambuzi.uninstall.before_uninstall"
# after_uninstall = "upande_tambuzi.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "upande_tambuzi.utils.before_app_install"
# after_app_install = "upande_tambuzi.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "upande_tambuzi.utils.before_app_uninstall"
# after_app_uninstall = "upande_tambuzi.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "upande_tambuzi.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#   "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#   "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#   "ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events
# doc_events = {
#   "*": {
#       "on_update": "method",
#       "on_cancel": "method",
#       "on_trash": "method"
#   }
# }
doc_events = {
    "Sales Order": {
        "on_submit":
        "upande_tambuzi.server_scripts.pick_list_automation.create_pick_list_for_sales_order",
        "before_submit":
        "upande_tambuzi.upande_tambuzi.custom.sales_order_custom.validate_customer_check_limit",
        "on_update":
        "upande_tambuzi.server_scripts.so_delivery_warehouse.handle_sales_order_approval",
        "on_cancel":
        "upande_tambuzi.server_scripts.so_delivery_warehouse.handle_sales_order_cancellation"
    },
    "Consolidated Pack List": {
        "on_submit":
        "upande_tambuzi.server_scripts.create_sales_invoice.create_sales_invoice_from_packlist",
        "before_submit":
        "upande_tambuzi.server_scripts.completion_percentage.validate_completion_percentage"
    },
    "Sales Invoice": {
        "on_submit":
        "upande_tambuzi.server_scripts.sinv_approved_by.set_approved_by"
    },
    "Farm Pack List": {
        "before_cancel":
        "upande_tambuzi.server_scripts.fpl_to_cpl_link.before_cancel"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    # "cron": {
    #     "* * * * *": [
    #         "upande_tambuzi.tasks.transfer_stock"
    #     ]
    # },
    # "all": [
    #     "upande_tambuzi.tasks.transfer_stock"
    # ],
    "daily": ["upande_tambuzi.tasks.transfer_stock"],
    #   "hourly": [
    #       "upande_tambuzi.tasks.hourly"
    #   ],
    #   "weekly": [
    #       "upande_tambuzi.tasks.weekly"
    #   ],
    #   "monthly": [
    #       "upande_tambuzi.tasks.monthly"
    #   ],
}

# Testing
# -------

# before_tests = "upande_tambuzi.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#   "frappe.desk.doctype.event.event.get_events": "upande_tambuzi.event.get_events"
# }

override_class = {
    "erpnext.controllers.taxes_and_totals.calculate_taxes_and_totals":
    "upande_tambuzi.overrides.standard_system_rate.CustomTaxesAndTotals"
}

whitelisted_methods = {
    "get_item_group_price":
    "upande_tambuzi.server_scripts.fetch_item_grp_price.get_item_group_price",
    "create_sales_invoice":
    "upande_tambuzi.server_scripts.create_sales_invoice.create_sales_invoice"
}

#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#   "Task": "upande_tambuzi.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["upande_tambuzi.utils.before_request"]
# after_request = ["upande_tambuzi.utils.after_request"]

# Job Events
# ----------
# before_job = ["upande_tambuzi.utils.before_job"]
# after_job = ["upande_tambuzi.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#   {
#       "doctype": "{doctype_1}",
#       "filter_by": "{filter_by}",
#       "redact_fields": ["{field_1}", "{field_2}"],
#       "partial": 1,
#   },
#   {
#       "doctype": "{doctype_2}",
#       "filter_by": "{filter_by}",
#       "partial": 1,
#   },
#   {
#       "doctype": "{doctype_3}",
#       "strict": False,
#   },
#   {
#       "doctype": "{doctype_4}"
#   }
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#   "upande_tambuzi.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
#   "Logging DocType Name": 30  # days to retain logs
# }

fixtures = [{
    "dt":
    "Server Script",
    "filters": [[
        "name", "in",
        [
            "Stock Entry Script", "Stock Entry After Save", "Scan Timestamp",
            "Harvest Stock Entry", "Automate Rejects Material Issue",
            "Create Box Labels"
        ]
    ]]
}, {
    "dt":
    "Client Script",
    "filters": [[
        "name", "in",
        [
            "Qr Code gen", "Close Box Button", "Scan Via Honeywell",
            "Scan Data Field Listener", "Scan QR Button",
            "Populate Number of Items", "Grading Stock Entry",
            "Field Rejects Stock Entry", "Archive Employee",
            "Transfer Grading Stock", "Generate Bucket Codes", "Harvest Scan",
            "New Form After Save", "Remove Read Only on Field",
            "Ensure Bucket Is Scanned On Save", "Field Rejects Stock Entry",
            "Hide Filter Button", "Ensure Uppercase in Bay Field",
            "Grading Traceability Symbols"
        ]
    ]]
}, {
    "dt":
    "DocType",
    "filters": [[
        "name", "in",
        [
            "Scan Location", "QR Code", "Packing List", "Pack List Item",
            "Scan", "Farm", "Box Label", "Box Label Item", "Label Print",
            "Bucket QR Code", "Bunch QR Code", "Grader QR Code", "Harvest",
            "Scanned Items", "Scan Check", "Scan Check List", "QR Sequence",
            "Rejection Reason"
        ]
    ]]
}, {
    "dt":
    "Print Format",
    "filters": [[
        "name", "in",
        [
            "QR Code Only", "Box Label", "Harvest Label",
            "Grader QR Print Format", "Bunch QR Code",
            "Trial Bunch Print Format", "Grader QR Print format 2",
            "Harvest Label 2"
        ]
    ]]
}, {
    "dt": "Custom DocPerm"
}, {
    "dt":
    "Report",
    "filters": [[
        "name", "in",
        ["Field Rejects Report", "Packhouse Discards/Rejects Report"]
    ]]
}]
