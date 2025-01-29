frappe.ui.form.on('Packing List', {
    refresh: function (frm) {
        frm.add_custom_button(__('Fetch Available Items'), function () {
            if (!frm.doc.warehouse) {
                frappe.msgprint(__('Please select a Warehouse first.'));
                return;
            }

            frappe.call({
                method: "upande_tambuzi.upande_tambuzi.doctype.packing_list.packing_list.get_available_items",
                args: {
                    warehouse: frm.doc.warehouse
                },
                callback: function (r) {
                    if (r.message) {
                        // Clear existing items in the child table
                        frm.clear_table('items');

                        // Loop through the fetched items and add them to the table
                        r.message.forEach(item => {
                            let child = frm.add_child('items');
                            child.item_code = item.item_code;
                            child.item_name = item.item_name;
                            child.qty = item.actual_qty;
                        });

                        // Refresh the table to show changes
                        frm.refresh_field('items');
                        frappe.msgprint(__('Items fetched successfully! Check the child table.'));
                    } else {
                        frappe.msgprint(__('No items found for the selected Warehouse.'));
                    }
                }
            });
        });
    }
});
