frappe.listview_settings[ "Vibe Theme" ] = {
	onload: function( listview ){
		listview.page.add_inner_button( __( "Theme Usage" ), () => {
			frappe.set_route( "query-report", "Theme Usage", { } );
		}, __( "Reports" ) );
	}
}
