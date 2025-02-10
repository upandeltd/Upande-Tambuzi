frappe.ui.form.on('Farm Pack List', {
    refresh: function(frm) {
        console.log('docstatus:', frm.doc.docstatus);  // Debugging log

        // Ensure button only appears for submitted documents and is not already closed
        if (!frm.is_new() && frm.doc.docstatus === 1 && !frm.doc.is_closed) {
            frm.clear_custom_buttons();  // Prevent duplicate buttons
            frm.add_custom_button(__('Close'), () => {
                create_consolidated_pack_list(frm);
            }).addClass('btn-primary close-btn');  // Add custom class
        }
    }
});

function create_consolidated_pack_list(frm) {
    frappe.call({
        method: 'upande_tambuzi.upande_tambuzi.doctype.farm_pack_list.farm_pack_list.create_consolidated_pack_list',
        args: {
            farm_pack_list: frm.doc.name
        },
        callback: function(r) {
            if (!r.exc) {
                frappe.show_alert({
                    message: __('Consolidated Pack List created successfully'),
                    indicator: 'green'
                });

                // Update button appearance and disable it
                $(".close-btn").text("Closed").removeClass("btn-primary").addClass("btn-success").prop("disabled", true);

                // Update the form field to mark it as closed
                frm.set_value("custom_is_closed", 1);
                frm.save();  // Save the status change
            }
        }
    });
}
