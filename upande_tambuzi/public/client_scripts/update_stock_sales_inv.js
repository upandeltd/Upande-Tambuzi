// Copyright (c) 2025, Upande Limited and contributors
// For license information, please see license.txt



frappe.ui.form.on('Sales Invoice', {
    onload: function(frm) {
        frm.set_value('update_stock', 1);
    },
    validate: function(frm) {
        if (!frm.doc.update_stock) {
            frm.set_value('update_stock', 1);
        }
    }
});
