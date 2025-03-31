// frappe.ui.form.on('Sales Order Item', {
//     custom_length(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];  
        
//         if (row.item_group && row.custom_length) {
//             frappe.call({
//                 method: "upande_tambuzi.server_scripts.fetch_item_grp_price.get_item_group_price",
//                 args: {
//                     item_group: row.item_group,
//                     length: row.custom_length,
//                     currency: frm.doc.currency
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         frappe.model.set_value(cdt, cdn, "rate", r.message);
//                         frappe.model.set_value(cdt, cdn, "stock_uom_rate", r.message);
//                         frappe.model.set_value(cdt, cdn, "amount", r.message * (row.stock_qty || 0));  
//                     } else {
//                         frappe.model.set_value(cdt, cdn, "rate", 0);
//                         frappe.model.set_value(cdt, cdn, "stock_uom_rate", 0);
//                         frappe.model.set_value(cdt, cdn, "amount", 0);
//                         frappe.msgprint(`No price found for this customer's currency or the selected item. Please set a price to proceed!`);
//                     }
//                     frm.refresh_field("items");  
//                 }
//             });
//         }
//     },
//     rate(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         frappe.model.set_value(cdt, cdn, "stock_uom_rate", row.rate);
//         frappe.model.set_value(cdt, cdn, "amount", row.rate * (row.stock_qty || 0));  
//     },
//     stock_qty(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         frappe.model.set_value(cdt, cdn, "amount", row.rate * (row.stock_qty || 0));  
//     }
// });
