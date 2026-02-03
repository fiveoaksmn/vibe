// Copyright (c) 2026, Five Oaks, Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on( "Vibe Message", {
	refresh( frm ){
        if( ! frm.is_new() && frm.doc.status === "Draft" ){
            frm.add_custom_button( __( "Send" ), function(){
                frappe.call( {
                    method: "send_message",
                    doc: frm.doc,
                    callback: function(r) {
                        frm.reload_doc();
                    }
                } );
            } );
        }
	},
});
