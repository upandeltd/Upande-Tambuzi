frappe.ui.form.on('Sales Order Item', {
    custom_length(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.item_group && row.custom_length) {
            frappe.call({
                method: 'upande_tambuzi.server_scripts.fetch_item_grp_price.get_item_group_price',
                args: {
                    item_group: row.item_group,
                    length: row.custom_length
                },
                callback: function(r) {
                    console.log(r);
                    if (r.message) {
                        console.log(r.message);
                        frappe.model.set_value(cdt, cdn, 'rate', r.message);
                    } else {
                        frappe.model.set_value(cdt, cdn, 'rate', 0); // Default to 0
                        frappe.msgprint(`No price found. Please set the price to proceed!`); 
                    }
                }
            });
        }
    }
});
