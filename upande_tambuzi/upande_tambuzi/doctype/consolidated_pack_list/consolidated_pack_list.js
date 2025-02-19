frappe.listview_settings["Consolidated Pack List"] = {
    onload: function (listview) {
        listview.page.add_inner_button("Create Dispatch Form", function() {
            let selected_docs = listview.get_checked_items();
            
            if (!selected_docs.length) {
                frappe.msgprint(__("Please select at least one Consolidated Pack List"));
                return;
            }
            
            assign_multiple_cpls_to_dispatch(selected_docs);
        });
    }
};

function assign_multiple_cpls_to_dispatch(selected_docs) {
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
                process_bulk_cpl_assignment(selected_docs, values.selected_dispatch);
            }, __("Assign Selected CPLs"), __("Assign"));
        }
    });
}

function process_bulk_cpl_assignment(selected_docs, selected_dispatch) {
    let grouped_items = {};

    let fetch_cpl_data = selected_docs.map(cpl => {
        return new Promise(resolve => {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Consolidated Pack List",
                    name: cpl.name
                },
                callback: function(response) {
                    if (response.message) {
                        let cpl_doc = response.message;
                        let cpl_items = cpl_doc.items || [];

                        cpl_items.forEach(item => {
                            let key = `${item.customer_id}-${item.item_group}-${item.s_number}-${item.delivery_point}`;

                            if (!grouped_items[key]) {
                                grouped_items[key] = {
                                    consolidated_pack_list_id: selected_dispatch,
                                    customer_id: item.customer_id,
                                    item_group: item.item_group,
                                    no_of_boxes: 1,
                                    s_number: item.s_number,
                                    delivery_point: item.delivery_point,
                                    cpl_item: [item.name]
                                };
                            } else {
                                grouped_items[key].no_of_boxes += 1;
                                grouped_items[key].cpl_item.push(item.name);
                            }
                        });
                    }
                    resolve();
                }
            });
        });
    });

    Promise.all(fetch_cpl_data).then(() => {
        let dispatch_items = Object.values(grouped_items);
        update_bulk_dispatch_form(selected_docs, selected_dispatch, dispatch_items);
    });
}

function update_bulk_dispatch_form(selected_docs, dispatch_name, dispatch_items) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Dispatch Form",
            name: dispatch_name
        },
        callback: function(response) {
            if (!response.message) {
                frappe.msgprint(__("Error: Could not load Dispatch Form."));
                return;
            }

            let df_doc = response.message;
            
            // Initialize dispatch_form_item if it doesn't exist
            if (!df_doc.dispatch_form_item) {
                df_doc.dispatch_form_item = [];
            }

            // Create new array with existing items (if any) plus new items
            let new_items = [];
            
            // Add existing items if any
            if (df_doc.dispatch_form_item && Array.isArray(df_doc.dispatch_form_item)) {
                new_items = [...df_doc.dispatch_form_item];
            }
            
            // Add new items
            dispatch_items.forEach(item => {
                new_items.push({
                    consolidated_pack_list_id: item.consolidated_pack_list_id,
                    customer_id: item.customer_id,
                    item_group: item.item_group,
                    no_of_boxes: item.no_of_boxes,
                    s_number: item.s_number,
                    delivery_point: item.delivery_point,
                    doctype: 'Dispatch Form Item' // Add doctype for child table
                });
            });

            // Update the document with new items
            df_doc.dispatch_form_item = new_items;
            
            // Update total boxes count
            df_doc.no_of_boxes = new_items.reduce((sum, item) => sum + item.no_of_boxes, 0);

            frappe.call({
                method: "frappe.client.save",
                args: { doc: df_doc },
                callback: function(save_result) {
                    if (save_result.message) {
                        frappe.show_alert({
                            message: __("CPLs successfully assigned to Dispatch Form"),
                            indicator: 'green'
                        }, 15);

                        // Update all selected CPLs to dispatched status
                        let update_promises = selected_docs.map(cpl => {
                            return new Promise(resolve => {
                                frappe.call({
                                    method: "frappe.client.set_value",
                                    args: {
                                        doctype: "Consolidated Pack List",
                                        name: cpl.name,
                                        fieldname: {
                                            "custom_dispatched": 1,
                                            "custom_dispatch_status": "Dispatched"
                                        }
                                    },
                                    callback: function() {
                                        resolve();
                                    }
                                });
                            });
                        });

                        Promise.all(update_promises).then(() => {
                            frappe.show_alert({
                                message: __("All selected CPLs have been marked as dispatched"),
                                indicator: 'green'
                            }, 15);
                            
                            // Refresh the list view
                            cur_list.refresh();
                        });
                    } else {
                        frappe.msgprint(__("Error saving Dispatch Form: ") + save_result.exc);
                    }
                }
            });
        }
    });
}