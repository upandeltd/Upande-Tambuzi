frappe.ui.form.on('Farm Pack List', {
    refresh: function(frm) {
        // Only show close button if document is submitted and not already closed
        if(frm.doc.docstatus === 1 && frm.doc.custom_status !== 'Closed') {
            let closeButton = frm.add_custom_button('Close', () => {
                // Disable the button immediately to prevent multiple clicks
                closeButton.prop('disabled', true);
                
                // Confirm before proceeding
                frappe.confirm(
                    'Are you sure you want to close this Farm Pack List? Closing it updates or creates a consolidated pack list',
                    () => {
                        frappe.call({
                            method: 'upande_tambuzi.upande_tambuzi.doctype.farm_pack_list.farm_pack_list.close_farm_pack_list',
                            args: {
                                'farm_pack_list': frm.doc.name
                            },
                            callback: function(r) {
                                if(!r.exc) {
                                    // After closing, process the CPL
                                    frappe.call({
                                        method: 'upande_tambuzi.upande_tambuzi.doctype.farm_pack_list.farm_pack_list.process_consolidated_pack_list',
                                        args: {
                                            'farm_pack_list': frm.doc.name,
                                            'sales_order': frm.doc.sales_order_id
                                        },
                                        callback: function(r) {
                                            if(!r.exc) {
                                                // Update the status in the UI
                                                frm.set_value('custom_status', 'Closed');
                                                frm.save();
                                                frm.reload_doc();
                                                
                                                frappe.show_alert({
                                                    message: 'Farm Pack List closed and Consolidated Pack List updated successfully',
                                                    indicator: 'green'
                                                });
                                                
                                                // Remove the close button
                                                frm.remove_custom_button('Close');
                                            } else {
                                                // Re-enable the button if there was an error
                                                closeButton.prop('disabled', false);
                                            }
                                        }
                                    });
                                } else {
                                    // Re-enable the button if there was an error
                                    closeButton.prop('disabled', false);
                                }
                            }
                        });
                    },
                    () => {
                        // Re-enable the button if user cancels
                        closeButton.prop('disabled', false);
                    }
                );
            });
        }
    }
});