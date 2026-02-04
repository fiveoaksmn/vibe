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

	# Use Werkzeug Response to bypass JSON handling
	return Response( css_content, mimetype="text/css" )
