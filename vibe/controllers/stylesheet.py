import frappe
from frappe import _
from werkzeug.wrappers import Response


@frappe.whitelist( allow_guest=True )
def css():
    css_content = ""
    minify = False

    vibeTheme = frappe.qb.DocType( "Vibe Theme" )
    rows = (
        frappe.qb.from_( vibeTheme )
        .select( vibeTheme.name )
        .where( vibeTheme.disabled == 0 )
    ).run( as_dict=True )
    for row in rows:
        theme = frappe.get_doc( "Vibe Theme", row.name )
        css_content += theme.get_css( minify=minify )

    # Address defect in which the "Light", "Dark", and "Automatic" theme previews have the navbar inheriting the currently selected theme
    css_content += ".theme-grid div[data-theme=\"light\"] .navbar{background-color: #ededed !important;} .theme-grid div[data-theme=\"dark\"] .navbar{background-color: black !important;}"

    # Add any custom CSS
    settings = frappe.get_doc( "Vibe Settings" )
    if minify and settings.custom_css_minified is not None:
        css_content += " " + settings.custom_css_minified
    if ( not minify or settings.custom_css_minified is None ) and settings.custom_css is not None:
        css_content += " " + settings.custom_css

    # Use Werkzeug Response to bypass JSON handling
    return Response( css_content, mimetype="text/css" )
