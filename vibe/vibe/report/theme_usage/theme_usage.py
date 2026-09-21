import frappe
from frappe import _
from frappe.query_builder.functions import Count


FRAPPE_THEMES = ( "Light", "Dark", "Automatic" )


def execute( filters=None ):
    User = frappe.qb.DocType( "User" )
    VibeTheme = frappe.qb.DocType( "Vibe Theme" )

    count_all = Count( '*' ).as_( "count" )
    rows = (
        frappe.qb.from_( User )
        .left_join( VibeTheme ).on( User.desk_theme == VibeTheme.name )
        .select( User.desk_theme, VibeTheme.theme_title, count_all )
        .where( User.enabled == 1 ) # enabled users only
        .groupby( User.desk_theme, VibeTheme.theme_title )
    ).run( as_dict=True )

    for row in rows:
        # If the user doesn't have a theme set, Frappe will default to Light
        if not row.desk_theme:
            row.desk_theme = "Light"

        if row.theme_title:
            continue
        if row.desk_theme in FRAPPE_THEMES:
            row.theme_title = f"Frappe {row.desk_theme}"
        else:
            # Points at a Vibe Theme that no longer exists
            row.theme_title = row.desk_theme

    # Sort alphabetically but with the Frappe defaults at the top
    rows.sort( key = lambda r: ( not r.theme_title.startswith( "Frappe " ), r.theme_title ) )
    # Sort alphabetically
    # rows.sort( key=lambda r: r.theme_title )

    columns = [
        {
            "fieldname": "theme_title",
            "label": _( "Theme" ),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "count",
            "label": _( "Usage" ),
            "fieldtype": "Int",
            "width": 100
        }
    ]

    return columns, rows
