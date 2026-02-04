// Copyright (c) 2026, Five Oaks, Inc and contributors
// For license information, please see license.txt

frappe.ui.form.on( "Vibe Theme", {
	refresh( frm ){
		frm.events.update_color_options( frm );

		$( "select[data-fieldname$='_color']" ).on( "change", function(){
        	// 'this' is the select element
    	    const value = $( this ).val();
	        console.log('Color changed:', value);
	    } );
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

		const fields = [
			"navbar_background_color", "navbar_icon_color", "nabar_breadcrumb_color", "navbar_title_color",
			"sidebar_background_color",
			"sidebar_header_background_color", "sidebar_header_title_color", "sidebar_header_subtitle_color", "sidebar_header_hover_background_color", "sidebar_header_hover_title_color", "sidebar_header_hover_subtitle_color", "sidebar_header_active_background_color", "sidebar_header_active_title_color", "sidebar_header_active_subtitle_color",
			"sidebar_middle_icon_color", "sidebar_middle_item_color", "sidebar_middle_item_suffix_color", "sidebar_middle_hover_background_color", "sidebar_middle_hover_icon_color", "sidebar_middle_hover_item_color", "sidebar_middle_hover_item_suffix_color", "sidebar_middle_active_background_color", "sidebar_middle_active_icon_color", "sidebar_middle_active_item_color", "sidebar_middle_active_item_suffix_color",
			"sidebar_footer_background_color", "sidebar_footer_title_color", "sidebar_footer_subtitle_color", "sidebar_footer_hover_background_color", "sidebar_footer_hover_title_color", "sidebar_footer_hover_subtitle_color"
		];
		fields.forEach( field => {
			frm.set_df_property( field, "options", options );
		} )
	}
} );


frappe.ui.form.on( "Vibe Palette", {
    palette_add( frm, cdt, cdn ){
		frm.events.update_color_options( frm );
    },

    palette_remove(frm, cdt, cdn) {
		frm.events.update_color_options( frm );
    },

    color_name( frm, cdt, cdn ){
		frm.events.update_color_options( frm );
    },

    color( frm, cdt, cdn ){
		frm.events.update_color_options( frm );
    }
} );
