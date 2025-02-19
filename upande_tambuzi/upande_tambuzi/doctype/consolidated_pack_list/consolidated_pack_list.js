frappe.listview_settings["Consolidated Pack List"] = {
    onload: function (listview) {
        listview.page.add_inner_button("Create to Dispatch Form", function () {
            let selected_docs = listview.get_checked_items();

            if (!selected_docs.length) {
                frappe.msgprint(__("Please select at least one Consolidated Pack List"));
                return;
            }

            validate_and_process_cpls(selected_docs);
        });
    }
};

function validate_and_process_cpls(selected_docs) {
    let validation_promises = selected_docs.map(cpl => {
        return new Promise(resolve => {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Consolidated Pack List",
                    name: cpl.name,
                    fields: ["name", "custom_dispatched"]
                },
                callback: function (response) {
                    if (response.message && response.message.custom_dispatched) {
                        resolve({ is_dispatched: true, cpl_id: cpl.name });
                    } else {
                        resolve({ is_dispatched: false, cpl_id: cpl.name });
                    }
                }
            });
        });
    });

    Promise.all(validation_promises).then(results => {
        let dispatched_cpls = results.filter(result => result.is_dispatched);

        if (dispatched_cpls.length > 0) {
            let cpl_list = dispatched_cpls.map(cpl => cpl.cpl_id).join(", ");
            frappe.msgprint(__(`Cannot process already dispatched CPLs: ${cpl_list}`));
            return;
        }

        process_bulk_cpl_assignment(selected_docs);
    });
}

function process_bulk_cpl_assignment(selected_docs) {
    let all_items = [];

    let fetch_cpl_data = selected_docs.map(cpl => {
        return new Promise(resolve => {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Consolidated Pack List",
                    name: cpl.name
                },
                callback: function (response) {
                    if (response.message) {
                        let cpl_doc = response.message;
                        let cpl_row_count = cpl_doc.items ? cpl_doc.items.length : 0;

                        if (cpl_doc.items && cpl_doc.items.length) {
                            cpl_doc.items.forEach(item => {
                                all_items.push({
                                    customer_id: item.customer_id,
                                    bunch_uom: item.bunch_uom,
                                    bunch_qty: item.bunch_qty,
                                    box_id: item.box_id,
                                    item_group: item.item_group,
                                    no_of_boxes: cpl_row_count, // Set no_of_boxes to count of items in CPL
                                    s_number: item.s_number,
                                    delivery_point: item.delivery_point,
                                    sales_order_id: item.sales_order_id || "N/A",
                                    consolidated_pack_list: cpl_doc.name
                                });
                            });
                        }
                    }
                    resolve();
                }
            });
        });
    });

    Promise.all(fetch_cpl_data).then(() => {
        create_new_dispatch_form(selected_docs, all_items);
    });
}

function create_new_dispatch_form(selected_docs, dispatch_items) {
    frappe.model.with_doctype("Dispatch Form", function () {
        let dispatch_form = frappe.model.get_new_doc("Dispatch Form");

        dispatch_items.forEach(item => {
            let new_row = frappe.model.add_child(dispatch_form, "dispatch_form_item");
            new_row.customer_id = item.customer_id;
            new_row.item_group = item.item_group;
            new_row.item_code = item.item_code;
            new_row.no_of_boxes = item.no_of_boxes;
            new_row.s_number = item.s_number;
            new_row.delivery_point = item.delivery_point;
            new_row.consolidated_pack_list = item.consolidated_pack_list;
            new_row.sales_order_id = item.sales_order_id;
            new_row.box_id = item.box_id;
            new_row.bunch_uom = item.bunch_uom;
            new_row.bunch_qty = item.bunch_qty;
        });

        dispatch_form.no_of_boxes = dispatch_items.length; // Total number of items as rows

        frappe.call({
            method: "frappe.client.insert",
            args: { doc: dispatch_form },
            callback: function (save_result) {
                if (save_result.message) {
                    let new_dispatch_id = save_result.message.name;
                    frappe.show_alert({
                        message: __(`CPLs successfully assigned to new Dispatch Form ${new_dispatch_id}`),
                        indicator: 'green'
                    }, 15);

                    let update_promises = selected_docs.map(cpl => {
                        return new Promise(resolve => {
                            frappe.call({
                                method: "frappe.client.set_value",
                                args: {
                                    doctype: "Consolidated Pack List",
                                    name: cpl.name,
                                    fieldname: { "custom_dispatched": 1, "custom_dispatch_status": "Dispatched" }
                                },
                                callback: function () { resolve(); }
                            });
                        });
                    });

                    Promise.all(update_promises).then(() => {
                        frappe.show_alert({
                            message: __("All selected CPLs have been marked as dispatched"),
                            indicator: 'green'
                        }, 15);
                        cur_list.refresh();
                    });
                } else {
                    frappe.msgprint(__("Error creating Dispatch Form: ") + save_result.exc);
                }
            }
        });
    });
}
