// frappe.ui.form.on('Farm Pack List', {
//     refresh: function(frm) {
//         console.log('docstatus:', frm.doc.docstatus);  // Debugging log

//         // Ensure button only appears for submitted documents
//         if (!frm.is_new() && frm.doc.docstatus === 1) {
//             frm.clear_custom_buttons();  // Prevent duplicate buttons
//             frm.add_custom_button(__('Close'), () => {
//                 create_consolidated_pack_list(frm);
//             });
//         }
//     }
// });

// function create_consolidated_pack_list(frm) {
//     frappe.call({
//         method: 'upande_tambuzi.upande_tambuzi.doctype.farm_pack_list.farm_pack_list.create_consolidated_pack_list',
//         args: {
//             farm_pack_list: frm.doc.name
//         },
//         callback: function(r) {
//             if (!r.exc) {
//                 frappe.show_alert({
//                     message: __('Consolidated Pack List created successfully'),
//                     indicator: 'green'
//                 });
//                 frm.reload_doc();  // Refresh the document
//             }
//         }
//     });
// }
