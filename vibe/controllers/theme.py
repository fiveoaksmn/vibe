import frappe
from frappe.query_builder.functions import Lower


@frappe.whitelist()
def switch_theme( theme ):
	vibeTheme = frappe.qb.DocType( "Vibe Theme" )
	qb = (
		frappe.qb.from_( vibeTheme )
		.select( vibeTheme.theme_title )
		.where( vibeTheme.disabled == 0 )
		.where( Lower( vibeTheme.theme_title ) == theme.lower() )
	)

	# Published only if the user is not a developer
	if "System Manager" not in frappe.get_roles( frappe.session.user ):
		qb = qb.where( vibeTheme.published == 1 )

	rows = qb.run( as_dict=True )
	if len( rows ) > 0:
		frappe.db.set_value( "User", frappe.session.user, "desk_theme", rows[ 0 ].theme_title )


@frappe.whitelist()
def list():
	vibeTheme = frappe.qb.DocType( "Vibe Theme" )
	qb = (
		frappe.qb.from_( vibeTheme )
		.select( Lower( vibeTheme.theme_title ).as_( "name" ), vibeTheme.theme_title.as_( "label" ), vibeTheme.description.as_( "info" ) )
		.where( vibeTheme.disabled == 0 )
	)

	# Published only if the user is not a developer
	if "System Manager" not in frappe.get_roles( frappe.session.user ):
		qb = qb.where( vibeTheme.published == 1 )

	rows = qb.run( as_dict=True )

	return {
		"themes": rows
	}


def sync_themes():
	vibeTheme = frappe.qb.DocType( "Vibe Theme" )
	qb = (
		frappe.qb.from_( vibeTheme )
		.select( vibeTheme.theme_title )
		.where( vibeTheme.disabled == 0 )
		.orderby( vibeTheme.theme_title )
	)

	# Published only if the user is not a developer
	if "System Manager" not in frappe.get_roles( frappe.session.user ):
		qb = qb.where( vibeTheme.published == 1 )

	themes = qb.run( pluck=True )
	themes = [ "Light", "Dark", "Automatic" ] + themes

	options = ""
	for theme in themes:
		if len( options ) > 0:
			options += "\n" + theme
		else:
			options += theme
	try:
		property = frappe.get_last_doc( "Property Setter", filters = { "name": "User-desk_theme-options" },
										order_by = "creation desc" )
		property.property = "options"
		if property.value != options:
			property.value = options
			property.save()
	except frappe.DoesNotExistError:
		property = frappe.new_doc( "Property Setter" )
		property.doctype_or_field = "DocField"
		property.doc_type = "User"
		property.field_name = "desk_theme"
		property.module = "Business"
		property.property = "options"
		property.value = options
		property.default_value = "Light"
		property.save()


def import_theme( theme_json ):
	# Confirm name provided
	if not theme_json.get( "name" ):
		frappe.throw( "Theme JSON is missing 'name'" )

	# Check if the theme exists
	changes = False
	try:
		doc = frappe.get_doc( "Vibe Theme", theme_json[ "name" ] )
	except frappe.DoesNotExistError:
		doc = frappe.new_doc( "Vibe Theme" )
		doc.theme_title = theme_json[ "name" ]
		changes = True

	# Don't continue if protected
	if doc.protect:
		return

	# Basic fields
	if doc.description != theme_json.get( "description" ):
		doc.description = theme_json.get( "description" )
		changes = True

	# Build palette lookup: "Green" -> "#709360"
	palette_lookup = { }
	verified = []
	for row in theme_json.get( "palette", [ ] ):
		if not row.get( "name" ) or not row.get( "color" ):
			continue
		palette_lookup[ row[ "name" ] ] = row[ "color" ]

		exists = False
		for color in doc.palette:
			if color.color_name == row[ "name" ]:
				exists = True
				verified.append( color.color_name )
				if color.color != row[ "color" ]:
					color.color = row[ "color" ]
					changes = True
				break

		if not exists:
			# Add to child table
			doc.append( "palette", {
				"color_name": row[ "name" ],
				"color": row[ "color" ]
			} )
			verified.append( row[ "name" ] )
			changes = True

	for i in range( len( doc.palette ) - 1, -1, -1 ):
		row = doc.palette[ i ]
		if row.get( "color_name" ) not in verified:
			doc.palette.pop( i )

	# Helper: resolve palette name -> hex (or keep hex if already hex)
	def resolve_color( value ):
		if not value:
			return None

		# already a hex code
		if isinstance( value, str ) and value.strip().startswith( "#" ):
			return value.strip()

		# palette name
		return palette_lookup.get( value, value )


	# Apply nested keys into fields like:
	# core.background_color -> core_background_color
	# navbar.icon_color -> navbar_icon_color
	# sidebar.header_hover_title_color -> sidebar_header_hover_title_color
	for group, group_values in theme_json.items():
		if group in ( "name", "description", "palette" ):
			continue

		if not isinstance( group_values, dict ):
			continue

		for key, value in group_values.items():
			fieldname = f"{group}_{key}"
			if doc.get( fieldname ) != value:
				doc.set( fieldname, resolve_color( value ) )
				changes = True

	if changes:
		doc.save( ignore_permissions = True )

	return doc
