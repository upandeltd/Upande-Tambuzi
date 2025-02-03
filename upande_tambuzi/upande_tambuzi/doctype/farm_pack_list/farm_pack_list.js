// frappe.ui.form.on('Farm Pack List', {
//     refresh: function(frm) {
//         if (!frm.doc.__islocal && frm.doc.docstatus === 1) {
//             frm.add_custom_button('Close', () => {
//                 create_consolidated_pack_list(frm);
//             });
//         }
//     }
// });

// function create_consolidated_pack_list(frm) {
//     frappe.call({
//         method: 'upande_tambuzi.upande_tambuzi.doctype.farm_pack_list.create_consolidated_pack_list',
//         args: {
//             farm_pack_list: frm.doc.name
//         },
//         callback: function(r) {
//             if (!r.exc) {
//                 frappe.show_alert({
//                     message: __('Consolidated Pack List created successfully'),
//                     indicator: 'green'
//                 });
//                 frm.reload_doc();
//             }
//         }
//     });
// }