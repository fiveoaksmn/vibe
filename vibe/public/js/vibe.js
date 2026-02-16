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

class VibeApp{

	constructor(){
		this.when_ready();
	}

	when_ready(){
		const $navbar = $( "#navbar-modal-search" );
        if( ! $navbar.length ){
            setTimeout( () => this.when_ready(), 100 );
            return;
        }
		this.message_listener();
		this.sticky_banner();
	}

	message_listener(){
		frappe.realtime.on( "vibe_message", ( data ) => {
			frappe.msgprint( {
				title: data.title,
				message: data.message,
				indicator: data.indicator
			} );
		} );
	}

	sticky_banner(){
		frappe.call( {
            method: "vibe.controllers.theme.sticky_banner",
            callback: ( response ) => {
                if( response?.message?.enabled ){
					const sidebar = document.querySelector( ".body-sidebar-container" );
					const main = document.querySelector( ".main-section" );
					if( ! sidebar || ! main ) return;

					// Encapsulate the layout in a wrapper and add the sticky bar above
					if( ! document.querySelector( ".desk-layout-wrapper" ) ){
						document.body.style.display = "flex";
						document.body.style.flexDirection = "column";
						document.querySelector( ".body-sidebar-container" )?.classList.add( "sticky" );
						document.querySelector( ".body-sidebar" )?.classList.add( "sticky" );
						document.querySelector( ".main-section" )?.classList.add( "sticky" );

						const wrapper = document.createElement( "div" );
						wrapper.className = "desk-layout-wrapper";
						sidebar.parentNode.insertBefore( wrapper, sidebar );
						wrapper.appendChild( sidebar );
						wrapper.appendChild( main );

						const banner = document.createElement( "div" );
						banner.className = "global-sticky-banner";
						banner.innerHTML  = response.message.content;
						banner.style.color = response.message.textColor;
						banner.style.backgroundColor = response.message.backgroundColor;
						document.body.prepend( banner );
					}
				}
            },
        } );

	}
}

$( document ).on( "app_ready", () => {
	const vibe = new VibeApp();
} );
