
$( document ).on( "app_ready", () => {
    frappe.realtime.on( "vibe_message", ( data ) => {
        frappe.msgprint( {
            title: data.title,
            message: data.message,
            indicator: data.indicator
        } );
    } );
} );