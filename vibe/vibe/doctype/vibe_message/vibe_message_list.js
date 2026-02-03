frappe.listview_settings[ "Vibe Message" ] = {
    onload( listview ){
        frappe.realtime.on( "vibe_message_test", ( data ) => {
            frappe.msgprint( {
                title: __( "Vibe Test Message" ),
                message: data.message,
                indicator: "blue"
            } );
        } );

        listview.page.add_inner_button( __( "Send Test Message" ), () => {
            open_send_message_dialog();
        } );
    }
};

function open_send_message_dialog() {
    const dialog = new frappe.ui.Dialog( {
        title: __( "Send Test Message" ),
        fields: [
            {
                fieldname: "message",
                fieldtype: "Text Editor",
                label: __( "Message" ),
                reqd: 1
            }
        ],
        primary_action_label: __( "Send" ),
        primary_action: ( values ) => {
            frappe.call({
                method: "vibe.vibe.doctype.vibe_message.vibe_message.send_test_message",
                args: {
                    message: values.message
                },
                freeze: true,
                callback: ( r ) => {
                    frappe.show_alert( {
                        message: __( "Message Sent. Please wait <strong>5 seconds</strong> to receive." ),
                        indicator: "green"
                    }, 5 );
                    dialog.hide();
                },
                error: ( err ) => {
                    console.error( err );
                    frappe.msgprint( __( "Failed to send message" ) );
                }
            } );
        },
        secondary_action_label: __( "Cancel" ),
        secondary_action: () => {
            dialog.hide();
        }
    } );
    dialog.show();
}
