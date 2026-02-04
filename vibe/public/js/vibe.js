frappe.provide( "frappe.ui" );

frappe.ui.ThemeSwitcher = class CustomThemeSwitcher extends frappe.ui.ThemeSwitcher {
    constructor() {
        super()
    }

    fetch_themes() {
		return new Promise(( resolve ) => {
			frappe.call( {
				method: "vibe.controllers.theme.list",
				callback: ( r ) => {
					this.themes = [
						{
							name: "light",
							label:("Frappe Light"),
							info:("Light Theme"),
						},
						{
							name: "dark",
							label:"Timeless Night",
							info:"Dark Theme",
						},
						{
							name: "automatic",
							label:"Automatic",
							info:"Uses system's theme to switch between light and dark mode",
						}
					];
					if( r.message.themes && Array.isArray( r.message.themes ) ){
						this.themes.push( ...r.message.themes );
					}
					resolve( this.themes );
				}
			} );
		});
	}
}


$( document ).on( "app_ready", () => {
    frappe.realtime.on( "vibe_message", ( data ) => {
        frappe.msgprint( {
            title: data.title,
            message: data.message,
            indicator: data.indicator
        } );
    } );
} );
