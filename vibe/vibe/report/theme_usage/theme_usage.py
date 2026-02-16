import frappe
from frappe import _
from frappe.query_builder.functions import Count


def execute( filters=None ):
    user = frappe.qb.DocType( "User" )
    vibeTheme = frappe.qb.DocType( "Vibe Theme" )

    count_all = Count( '*' ).as_( "count" )
    rows = (
        frappe.qb.from_( vibeTheme )
        .join( user ).on( vibeTheme.name == user.desk_theme )
        .select( vibeTheme.theme_title, count_all )
        .groupby( vibeTheme.theme_title )
        .orderby( vibeTheme.theme_title )
    ).run( as_dict=True )

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
