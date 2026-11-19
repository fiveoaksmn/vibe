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

    // Give up waiting for the desk after this many 100ms polls (10s)
    static MAX_READY_ATTEMPTS = 100;

	constructor(){
        // The realtime listener doesn't depend on the desk layout, so don't hold it behind when_ready()
        this.message_listener();
		this.when_ready();
	}

    // Frappe 16.50 reworked the desk navbar and sidebar
    static is_v16_50_plus(){
        const [ major = 0, minor = 0 ] = ( frappe.boot?.versions?.frappe || "0.0" ).split( "." ).map( Number );
        return major > 16 || ( major === 16 && minor >= 50 );
    }

    when_ready( attempt = 0 ){
        // Pre-16.50: wait for the navbar search (unchanged behavior)
        // 16.50+: #navbar-modal-search no longer exists, so wait for the main section instead
        const selector = VibeApp.is_v16_50_plus() ? ".main-section" : "#navbar-modal-search";
        if( ! document.querySelector( selector ) ){
            if( attempt < VibeApp.MAX_READY_ATTEMPTS ){
                setTimeout( () => this.when_ready( attempt + 1 ), 100 );
            }
            return;
        }
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
                if( ! response?.message?.enabled ) return;
                if( document.querySelector( ".desk-layout-wrapper" ) ) return;

					const sidebar = document.querySelector( ".body-sidebar-container" );
					const main = document.querySelector( ".main-section" );
					if( ! sidebar || ! main ) return;

                // Top-level <body> children holding the sidebar and main section.
                //    Pre-16.50 these are the sidebar and main section themselves (siblings under <body>);
                //    on 16.50+ they may sit inside a shared container, which is wrapped instead.
                const blocks = [ ];
                for( const el of [ sidebar, main ] ){
                    let block = el;
                    while( block.parentElement && block.parentElement !== document.body ){
                        block = block.parentElement;
                    }
                    if( block.parentElement === document.body && ! blocks.includes( block ) ){
                        blocks.push( block );
                    }
                }
                if( ! blocks.length ) return;

					// Encapsulate the layout in a wrapper and add the sticky bar above
						document.body.style.display = "flex";
						document.body.style.flexDirection = "column";
                sidebar.classList.add( "sticky" );
						document.querySelector( ".body-sidebar" )?.classList.add( "sticky" );
                main.classList.add( "sticky" );

						const wrapper = document.createElement( "div" );
						wrapper.className = "desk-layout-wrapper";
                blocks[ 0 ].parentNode.insertBefore( wrapper, blocks[ 0 ] );
                for( const block of blocks ){
                    wrapper.appendChild( block );
                }

						const banner = document.createElement( "div" );
						banner.className = "global-sticky-banner";
						banner.innerHTML  = response.message.content;
						banner.style.color = response.message.textColor;
						banner.style.backgroundColor = response.message.backgroundColor;
						document.body.prepend( banner );
            },
        } );
	}
}

$( document ).on( "app_ready", () => {
	const vibe = new VibeApp();
} );
