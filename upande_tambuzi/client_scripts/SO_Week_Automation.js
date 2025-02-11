frappe.ui.form.on('Sales Order', {
    delivery_date: function(frm) {
        console.log('Delivery Date changed event triggered');
        console.log('Current delivery date value:', frm.doc.delivery_date);
        
        if (frm.doc.delivery_date) {
            // Convert the delivery date string to a Date object
            let currentDate = frappe.datetime.str_to_obj(frm.doc.delivery_date);
            console.log('Converted date object:', currentDate);
            
            // Calculate the week number
            let startOfYear = new Date(currentDate.getFullYear(), 0, 1);
            console.log('Start of year:', startOfYear);
            
            let days = Math.floor((currentDate - startOfYear) / (24 * 60 * 60 * 1000));
            console.log('Days since start of year:', days);
            
            let weekNumber = Math.ceil((days + startOfYear.getDay() + 1) / 7);
            console.log('Calculated week number:', weekNumber);
            
            // Set the week field value using the correct fieldname
            frm.set_value('custom_week', weekNumber);
            
            // Refresh the field
            frm.refresh_field('custom_week');
        }
    },
    
    refresh: function(frm) {
        console.log('Form refreshed');
        console.log('Current delivery date:', frm.doc.delivery_date);
        console.log('Current week:', frm.doc.custom_week);
    }
});
