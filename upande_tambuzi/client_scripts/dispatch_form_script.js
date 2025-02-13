frappe.ui.form.on('Dispatch Form', {
    custom_consolidated_pack_list_id: function(frm) {
        console.log("Trigger fired for consolidated_pack_list_id");
        
        if (frm.doc.consolidated_pack_list_id) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'Consolidated Pack List',
                    name: frm.doc.custom_consolidated_pack_list_id,
                    fields: ['custom_customer', 'custom_item_group', 'consolidated_pack_items']
                },
                callback: function(response) {
                    console.log("Response received:", response);
                    
                    if (response.message) {
                        const doc = response.message;
                        
                        // Set customer ID and crop
                        frm.set_value('customer_id', doc.custom_customer);
                        frm.set_value('crop', doc.custom_item_group);
                        
                        // Calculate total boxes from consolidated_pack_items
                        let total_boxes = 0;
                        if (doc.consolidated_pack_items && doc.consolidated_pack_items.length) {
                            total_boxes = doc.consolidated_pack_items.reduce((sum, item) => {
                                return sum + (item.box_id ? parseFloat(item.box_id) : 0);
                            }, 0);
                        }
                        
                        // Set total boxes
                        frm.set_value('custom_no_of_boxes', total_boxes);
                        
                        frm.refresh();
                        frappe.show_alert({
                            message: 'Form populated successfully',
                            indicator: 'green'
                        });
                    }
                },
                error: function(err) {
                    console.error("Error:", err);
                    frappe.throw(__('Error fetching data'));
                }
            });
        }
    }
});