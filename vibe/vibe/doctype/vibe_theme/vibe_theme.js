// Copyright (c) 2026, Five Oaks, Inc and contributors
// For license information, please see license.txt

const VIBE_COLOR_FIELDS = [
	"core_primary_text_color", "core_secondary_text_color", "core_link_color",
	"core_background_color", "core_surface_color", "core_border_color",
	"core_primary_color", "core_secondary_color", "core_success_color", "core_danger_color", "core_warning_color", "core_info_color",
	"navbar_background_color", "navbar_icon_color", "navbar_breadcrumb_color", "navbar_title_color", "navbar_breadcrumb_separator_color",
	"sidebar_background_color",
	"sidebar_header_background_color", "sidebar_header_title_color", "sidebar_header_subtitle_color", "sidebar_header_hover_background_color", "sidebar_header_hover_title_color", "sidebar_header_hover_subtitle_color", "sidebar_header_active_background_color", "sidebar_header_active_title_color", "sidebar_header_active_subtitle_color",
	"sidebar_middle_icon_color", "sidebar_middle_item_color", "sidebar_middle_item_suffix_color", "sidebar_middle_hover_background_color", "sidebar_middle_hover_icon_color", "sidebar_middle_hover_item_color", "sidebar_middle_hover_item_suffix_color", "sidebar_middle_active_background_color", "sidebar_middle_active_icon_color", "sidebar_middle_active_item_color", "sidebar_middle_active_item_suffix_color",
	"sidebar_footer_background_color", "sidebar_footer_title_color", "sidebar_footer_subtitle_color", "sidebar_footer_hover_background_color", "sidebar_footer_hover_title_color", "sidebar_footer_hover_subtitle_color"
];

frappe.ui.form.on( "Vibe Theme", {
	refresh( frm ){
		frm.events.update_color_options( frm );
		frm.events.render_color_swatches( frm );
		frm.events.bind_color_swatch_updates( frm );

		if( ! frm.is_new() ){
			frm.add_custom_button( __( "Export" ), async() => {
				frappe.call( {
					method: "export_theme",
					doc: frm.doc, // calls the method on THIS document
					callback: ( r ) => {
						if( ! r.message ){
							frappe.msgprint( __( "No export data returned." ) );
							return;
						}

						// r.message should be JSON serializable (dict/list)
						download_json_file(
							r.message,
							`${filename_safe_theme_name( frm.doc.name )}.json`
						);
					},
				} );
			} );
		}
	},

    before_save: function( frm ){
        frm.events.clear_empty_rows( frm );
    },

	clear_empty_rows( frm ){
        // work the way up from the bottom
		for( let i = frm.doc.palette.length - 1; i >= 0; i-- ){
			let row = frm.doc.palette[ i ];
			if( ! row.color_name && ! row.color ){
				frm.doc.palette.splice( i, 1 );
			}
		}
    },

	update_color_options( frm ){
		const options = [ "" ];
		for( let i = 0; i < frm.doc.palette.length; i++ ){
			const row = frm.doc.palette[ i ];
			options.push( row.color_name );
		}

		VIBE_COLOR_FIELDS.forEach( field => {
			frm.set_df_property( field, "options", options );
		} )
	},

	// build a lookup of color_name -> color (hex/rgba string) from the palette child table
	get_palette_color_map( frm ){
		const map = {};
		( frm.doc.palette || [] ).forEach( row => {
			if( row.color_name ){
				map[ row.color_name ] = row.color;
			}
		} );
		return map;
	},

	// add/update/remove the swatch box next to the label for every color select
	render_color_swatches( frm ){
		const palette_map = frm.events.get_palette_color_map( frm );
		VIBE_COLOR_FIELDS.forEach( fieldname => {
			frm.events.update_color_swatch( frm, fieldname, palette_map );
		} );
	},

	// add/update/remove the swatch box for a single field
	// `value` is optional - pass it explicitly (e.g. straight off the <select>) when
	// frm.doc may not have caught up yet, such as inside a live "change" handler
	update_color_swatch( frm, fieldname, palette_map, value ){
		const field = frm.fields_dict[ fieldname ];
		if( ! field || ! field.$wrapper ){
			return;
		}

		if( ! palette_map ){
			palette_map = frm.events.get_palette_color_map( frm );
		}

		if( value === undefined ){
			value = frm.doc[ fieldname ];
		}

		const color = value ? palette_map[ value ] : null;

		let $swatch = field.$wrapper.find( `.vibe-color-swatch[data-fieldname="${fieldname}"]` );

		// no value (or the value has no matching palette color) -> no box
		if( ! color ){
			if( $swatch.length ){
				$swatch.remove();
			}
			return;
		}

		if( ! $swatch.length ){
			const $label = field.$wrapper.find( ".control-label" ).first();
			if( ! $label.length ){
				return;
			}

			$swatch = $( `<span class="vibe-color-swatch" data-fieldname="${fieldname}"></span>` );
			$swatch.css( {
				display: "inline-block",
				width: "10px",
				height: "10px",
				"margin-left": "6px",
				"border-radius": "2px",
				border: "1px solid rgba(0, 0, 0, 0.25)",
				"vertical-align": "middle"
			} );

			$label.append( $swatch );
		}

		$swatch.css( "background-color", color );
	},

	// keep swatches in sync as the color selects change, without stacking duplicate handlers on every refresh
	bind_color_swatch_updates( frm ){
		frm.$wrapper.off( "change.vibe_color_swatch", "select[data-fieldname$='_color']" );
		frm.$wrapper.on( "change.vibe_color_swatch", "select[data-fieldname$='_color']", function(){
			// 'this' is the select element - read its value directly rather than from
			// frm.doc, since frm.doc isn't guaranteed to be updated yet at this point
			const fieldname = $( this ).attr( "data-fieldname" );
			const value = $( this ).val();
			if( fieldname ){
				frm.events.update_color_swatch( frm, fieldname, null, value );
			}
		} );
	}
} );


frappe.ui.form.on( "Vibe Palette", {
    palette_add( frm, cdt, cdn ){
		frm.events.update_color_options( frm );
		frm.events.render_color_swatches( frm );
    },

    palette_remove(frm, cdt, cdn) {
		frm.events.update_color_options( frm );
		frm.events.render_color_swatches( frm );
    },

    color_name( frm, cdt, cdn ){
		frm.events.update_color_options( frm );
		frm.events.render_color_swatches( frm );
    },

    color( frm, cdt, cdn ){
		frm.events.update_color_options( frm );
		frm.events.render_color_swatches( frm );
    }
} );

function download_json_file( data, filename ){
	const jsonStr = JSON.stringify( data, null, 2 );
	const blob = new Blob( [ jsonStr ], { type: "application/json" } );
	const url = window.URL.createObjectURL( blob );

	const a = document.createElement( "a" );
	a.href = url;
	a.download = filename;

	document.body.appendChild( a );
	a.click();

	a.remove();
	window.URL.revokeObjectURL( url );
}

function filename_safe_theme_name( theme_name ){
  return ( theme_name || "" )
    .toString()
    .trim()
    .toLowerCase()
    .replace( /\s+/g, "-" )        // spaces -> dashes
    .replace( /[^a-z0-9-]/g, "" )  // remove special chars
    .replace( /-+/g, "-" )         // collapse multiple dashes
    .replace( /^-|-$/g, "" );      // trim leading/trailing dashes
}
