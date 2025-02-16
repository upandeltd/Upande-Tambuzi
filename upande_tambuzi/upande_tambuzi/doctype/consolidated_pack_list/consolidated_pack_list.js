frappe.ui.form.on('Consolidated Pack List', {
    refresh: function(frm) {
        // Only show button if CPL is not already dispatched
        if (frm.doc.docstatus === 1 && frm.doc.custom_dispatch_status !== "Dispatched") {
            frm.add_custom_button(__('Attach to Dispatch Form'), () => assign_to_dispatch_form(frm));
        }
    }
});

function assign_to_dispatch_form(frm) {
    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Dispatch Form",
            filters: { docstatus: 0 },
            fields: ["name"]
        },
        callback: function(response) {
            let dispatch_forms = response.message || [];
            if (!dispatch_forms.length) {
                frappe.msgprint(__("No available Dispatch Forms in pending status."));
                return;
            }

            let dispatch_options = dispatch_forms.map(df => df.name);

            frappe.prompt([
                {
                    label: "Select Dispatch Form",
                    fieldname: "selected_dispatch",
                    fieldtype: "Select",
                    options: dispatch_options,
                    reqd: 1
                }
            ], function(values) {
                process_cpl_assignment(frm, values.selected_dispatch);
            }, __("Assign CPL to Dispatch Form"), __("Assign"));
        }
    });
}

function process_cpl_assignment(frm, selected_dispatch) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Consolidated Pack List",
            name: frm.doc.name,
            fields: ["*", "items.custom_customer", "items.custom_item_group", "items.custom_s_number", "items.custom_delivery_point"]
        },
        callback: function(r) {
            if (!r.message) {
                frappe.msgprint(__("Error: Could not load CPL details"));
                return;
            }

            let cpl_doc = r.message;
            let cpl_items = cpl_doc.items || [];

            if (!cpl_items.length) {
                frappe.msgprint(__("No items found in CPL."));
                return;
            }

            let grouped_items = {};

            // Group items by customer and item group to merge them into one row
            cpl_items.forEach(item => {
                let key = `${item.custom_customer}-${item.custom_item_group}-${item.custom_s_number}-${item.custom_delivery_point}`;

                if (!grouped_items[key]) {
                    grouped_items[key] = {
                        custom_consolidated_pack_list_id: frm.doc.name,
                        custom_customer: item.custom_customer,
                        custom_item_group: item.custom_item_group,
                        no_of_boxes: 1, // Start with 1 box
                        custom_s_number: item.custom_s_number, // Fix: Fetch correctly
                        custom_delivery_point: item.custom_delivery_point, // Fix: Fetch correctly
                        cpl_item: [item.name] // Store item names in array for tracking
                    };
                } else {
                    grouped_items[key].no_of_boxes += 1; // Sum up the boxes
                    grouped_items[key].cpl_item.push(item.name); // Track multiple items
                }
            });

            let dispatch_items = Object.values(grouped_items);
            update_dispatch_form(frm, selected_dispatch, dispatch_items);
        }
    });
}

function update_dispatch_form(frm, dispatch_name, dispatch_items) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Dispatch Form",
            name: dispatch_name
        },
        callback: function(r) {
            if (!r.message) {
                frappe.msgprint(__("Error: Could not load Dispatch Form."));
                return;
            }

            let df_doc = r.message;

            // Append new items to existing Dispatch Form
            df_doc.dispatch_form_item = df_doc.dispatch_form_item.concat(dispatch_items);

            // Update total boxes count
            let total_boxes = df_doc.dispatch_form_item.reduce((sum, item) => sum + item.no_of_boxes, 0);
            df_doc.no_of_boxes = total_boxes;
            df_doc.custom_consolidated_pack_list_id = frm.doc.name;

            frappe.call({
                method: "frappe.client.save",
                args: { doc: df_doc },
                callback: function(save_result) {
                    if (save_result.message) {
                        frappe.show_alert({
                            message: __(`CPL: ${frm.doc.name} assigned to Dispatch Form: ${dispatch_name}`),
                            indicator: 'green'
                        }, 5);

                        // Mark CPL as dispatched
                        frappe.call({
                            method: "frappe.client.set_value",
                            args: {
                                doctype: "Consolidated Pack List",
                                name: frm.doc.name,
                                fieldname: {
                                    "custom_dispatched": 1,
                                    "custom_dispatch_status": "Dispatched"
                                }
                            },
                            callback: function() {
                                frm.reload_doc();
                            }
                        });
                    } else {
                        frappe.msgprint(__("Error saving Dispatch Form: ") + save_result.exc);
                    }
                }
            });
        }
    });
}
