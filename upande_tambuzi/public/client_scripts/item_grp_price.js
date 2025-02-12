// Copyright (c) 2025, Upande Limited and contributors
// For license information, please see license.txt  
//Test instance

frappe.ui.form.on('Sales Order', {});

frappe.ui.form.on('Sales Order Item', {
    custom_length(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.item_group && row.custom_length) {
            frappe.call({
                method: 'get_item_group_price',
                args: {
                    item_group: row.item_group,
                    length: row.custom_length,
                    currency: frm.doc.currency
                },
                callback: function(r) {
                    console.log(r);
                    if (r.message) {
                        console.log(r.message);
                        frappe.model.set_value(cdt, cdn, 'rate', r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, 'rate', 0); // Default to 0
                        frappe.msgprint(`No price found for this customer's currency or the following items. Please have the price set to proceed!`); 
                        // For any item with price zero.

                    }
                }
            });
        }
    }
});
