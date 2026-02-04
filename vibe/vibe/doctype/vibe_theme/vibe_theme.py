# Copyright (c) 2026, Five Oaks, Inc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re
import unicodedata


class VibeTheme( Document ):
	def validate( self ):
		if self.theme_title.lower() in [ "light", "dark", "automatic" ]:
			frappe.throw( f"Theme title '{self.theme_title}' is reserved." )

		self.theme_code = self.sanitize_name( self.theme_title )


	def get_css( self, minify=True ):
		css = self.generate_palette( minify=minify )

		### NAVBAR

		# Navbar Background
		css += self.generate_selector( [ ".page-head-content", ".navbar" ], [ { "property": "background-color", "value": "${{navbar_background_color}}", "important": True } ], minify=minify )

		# Navbar Icon
		css += self.generate_selector( [ ".navbar-breadcrumbs > li > a > svg" ], [ { "property": "color", "value": "${{navbar_icon_color}}", "important": True }, { "property": "stroke", "value": "${{navbar_icon_color}}" } ], minify=minify )

		# Navbar Breadcrumbs
		css += self.generate_selector( [ ".navbar-breadcrumbs > li > a:not(.disabled)" ], [ { "property": "color", "value": "${{nabar_breadcrumb_color}}" } ], minify=minify )

		# Navbar Page Title
		css += self.generate_selector( [ ".navbar-breadcrumbs > li > a.disabled" ], [ { "property": "color", "value": "${{navbar_title_color}}" } ], minify=minify )


		### SIDEBAR

		# Sidebar Background
		css += self.generate_selector( [ ".body-sidebar" ], [ { "property": "background-color", "value": "${{sidebar_background_color}}", "important": True } ], minify=minify )

		# Sidebar Header: Background
		css += self.generate_selector( [ ".sidebar-header" ], [ { "property": "background-color", "value": "${{sidebar_header_background_color}}" } ], minify=minify )

		# Sidebar Header: Title
		css += self.generate_selector( [ ".sidebar-header .header-title" ], [ { "property": "color", "value": "${{sidebar_header_title_color}}" } ], minify=minify )

		# Sidebar Header: Subtitle
		css += self.generate_selector( [ ".sidebar-header .header-subtitle" ], [ { "property": "color", "value": "${{sidebar_header_subtitle_color}}" } ], minify=minify )

		# Sidebar Header: Hover Background
		css += self.generate_selector( [ ".sidebar-header.hover" ], [ { "property": "background-color", "value": "${{sidebar_header_hover_background_color}}", "important": True }, { "property": "border-radius", "value": "8px" } ], minify=minify )

		# Sidebar Header: Hover Title
		css += self.generate_selector( [ ".sidebar-header.hover .header-title" ], [ { "property": "color", "value": "${{sidebar_header_hover_title_color}}" } ], minify=minify )

		# Sidebar Header: Hover Subtitle
		css += self.generate_selector( [ ".sidebar-header.hover .header-subtitle" ], [ { "property": "color", "value": "${{sidebar_header_hover_subtitle_color}}" } ], minify=minify )

		# Sidebar Header: Active Background
		css += self.generate_selector( [ ".sidebar-header.active-sidebar" ], [ { "property": "background-color", "value": "${{sidebar_header_active_background_color}}", "important": True }, { "property": "border-radius", "value": "8px" } ], minify=minify )

		# Sidebar Header: Active Title
		css += self.generate_selector( [ ".sidebar-header.active-sidebar .header-title" ], [ { "property": "color", "value": "${{sidebar_header_active_title_color}}" } ], minify=minify )

		# Sidebar Header: Active Subtitle
		css += self.generate_selector( [ ".sidebar-header.active-sidebar .header-subtitle" ], [ { "property": "color", "value": "${{sidebar_header_active_subtitle_color}}" } ], minify=minify )


		# Sidebar Middle: Icons
		css += self.generate_selector( [ ".sidebar-item-icon svg", ".collapse-sidebar-link svg" ], [ { "property": "color", "value": "${{sidebar_middle_icon_color}}" }, { "property": "stroke", "value": "${{sidebar_middle_icon_color}}" } ], minify=minify )

		# Sidebar Middle: Item
		css += self.generate_selector( [ ".standard-sidebar-item:not(.active-sidebar) .sidebar-item-label" ], [ { "property": "color", "value": "${{sidebar_middle_item_color}}" } ], minify=minify )

		# Sidebar Middle: Item Suffix
		css += self.generate_selector( [ ".sidebar-item-suffix .keyboard-shortcut", ".collapse-sidebar-link" ], [ { "property": "color", "value": "${{sidebar_middle_item_suffix_color}}" } ], minify=minify )

		# Sidebar Middle: Hover Background
		css += self.generate_selector( [ ".body-sidebar .standard-sidebar-item:not(.active-sidebar):has(a:not(.section-break)):hover" ], [ { "property": "background-color", "value": "${{sidebar_middle_hover_background_color}}" } ], minify=minify )

		# Sidebar Middle: Hover Icon
		css += self.generate_selector( [ ".standard-sidebar-item:not(.active-sidebar):hover svg", ".collapse-sidebar-link:hover svg" ], [ { "property": "color", "value": "${{sidebar_middle_hover_icon_color}}" }, { "property": "stroke", "value": "${{sidebar_middle_hover_icon_color}}" } ], minify=minify )

		# Sidebar Middle: Hover Item
		css += self.generate_selector( [ ".standard-sidebar-item:not(.active-sidebar):hover .sidebar-item-label" ], [ { "property": "color", "value": "${{sidebar_middle_hover_item_color}}" } ], minify=minify )

		# Sidebar Middle: Hover Item Suffix
		css += self.generate_selector( [ ".standard-sidebar-item:not(.active-sidebar):hover .sidebar-item-suffix .keyboard-shortcut", ".collapse-sidebar-link:hover" ], [ { "property": "color", "value": "${{sidebar_middle_hover_item_suffix_color}}" } ], minify=minify )

		# Sidebar Middle: Active Background
		css += self.generate_selector( [ ".active-sidebar" ], [ { "property": "background-color", "value": "${{sidebar_middle_active_background_color}}" } ], minify=minify )

		# Sidebar Middle: Active Icon
		css += self.generate_selector( [ ".active-sidebar svg" ], [ { "property": "color", "value": "${{sidebar_middle_active_icon_color}}" }, { "property": "stroke", "value": "${{sidebar_middle_active_icon_color}}" } ], minify=minify )

		# Sidebar Middle: Active Item
		css += self.generate_selector( [ ".active-sidebar .sidebar-item-label" ], [ { "property": "color", "value": "${{sidebar_middle_active_item_color}}" } ], minify=minify )

		# Sidebar Middle: Active Item Suffix
		css += self.generate_selector( [ ".active-sidebar .sidebar-item-suffix" ], [ { "property": "color", "value": "${{sidebar_middle_active_item_suffix_color}}" } ], minify=minify )


		# Sidebar Footer: Background
		css += self.generate_selector( [ ".dropdown-navbar-user" ], [ { "property": "background-color", "value": "${{sidebar_footer_background_color}}" }, { "property": "border-radius", "value": "8px", "important": True } ], minify=minify )

		# Sidebar Footer: Title (aka user's username)
		css += self.generate_selector( [ ".avatar-name-email" ], [ { "property": "color", "value": "${{sidebar_footer_title_color}}" } ], minify=minify )

		# Sidebar Footer: Subtitle (aka user's email)
		css += self.generate_selector( [ ".standard-sidebar-item .keyboard-shortcut" ], [ { "property": "color", "value": "${{sidebar_footer_subtitle_color}}" } ], minify=minify )

		# Sidebar Footer: Hover Background
		css += self.generate_selector( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user:hover" ], [ { "property": "background-color", "value": "${{sidebar_footer_hover_background_color}}" }, { "property": "border-radius", "value": "8px", "important": True } ], minify=minify )

		# Sidebar Footer: Hover Title (aka user's username)
		css += self.generate_selector( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user:hover .avatar-name-email" ], [ { "property": "color", "value": "${{sidebar_footer_hover_title_color}}" } ], minify=minify )

		# Sidebar Footer: Hover Subtitle (aka user's email)
		css += self.generate_selector( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user:hover .avatar-name-email > .text-secondary" ], [ { "property": "color", "value": "${{sidebar_footer_hover_subtitle_color}}" } ], minify=minify )

		# Sidebar Footer: Fix Padding & Borders
		css += self.generate_selector( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user" ],
			[
				{ "property": "border-radius", "value": "8px", "important": True },
				{ "property": "padding-left", "value": "8px" },
				{ "property": "padding-right", "value": "8px" }
			], minify = minify
		)



		### Theme Preview

		css += self.generate_selector( [ ".theme-grid div[data-theme='" + self.theme_code + "'] .background" ], [ { "property": "background-color", "value": "white", "important": True } ], minify=minify, theme_selector=False )
		css += self.generate_selector( [ ".theme-grid div[data-theme='" + self.theme_code + "'] .navbar" ], [ { "property": "background-color", "value": "${{navbar_background_color}}", "important": True } ], minify=minify, theme_selector=False )
		css += self.generate_selector( [ ".theme-grid div[data-theme='" + self.theme_code + "'] .toolbar > .text" ], [ { "property": "background-color", "value": "${{sidebar_background_color}}", "important": True } ], minify=minify, theme_selector=False )

		return css


	# Generate the CSS of all the variables
	#    Args:
	#        minify (bool): If True, minify CSS output; else pretty-print.
	def generate_palette( self, minify=True ):
		# Start building lines
		lines = [ ]

		# Use quotes for data-theme to be safe
		theme_selector = f'[data-theme="{self.theme_code}"]'

		# Opening bracket
		if minify:
			lines.append( f"{theme_selector}{{" )
		else:
			lines.append( f"{theme_selector} {{" )

		# Generate each color variable
		for row in self.palette:
			var_name = "--" + self.sanitize_name( row.color_name )  # e.g., --primary-color
			var_value = row.color.strip()
			if minify:
				lines.append( f"{var_name}:{var_value};" )
			else:
				lines.append( f"    {var_name}: {var_value};" )

		# Closing bracket
		lines.append( "}" if minify else "}\n\n" )

		# Join lines
		css = "".join( lines ) if minify else "\n".join( lines )
		return css


	# Generate a CSS string from selectors and declarations, replacing variables.
	#    Args:
    #        selectors (list[str]): List of CSS selectors.
    #        declarations (list[dict]): List of {"property": str, "value": str}.
    #        minify (bool): If True, minify CSS output; else pretty-print.
	def generate_selector( self, selectors: list[str], declarations: list[dict], minify: bool = True, theme_selector: bool = True ) -> str:
		if not selectors or not declarations:
			return ""

		# Prepend the theme selector to every selector
		if theme_selector:
			theme_selector = f'[data-theme="{self.theme_code}"]'
			scoped_selectors = [ f"{theme_selector} {s}" for s in selectors ]
		else:
			scoped_selectors = selectors

		# Join selectors
		selector_str = ",".join( scoped_selectors ) if minify else ", ".join( scoped_selectors )

		# Start CSS block
		css_lines = [ f"{selector_str}{{" if minify else f"{selector_str} {{" ]

		for decl in declarations:
			prop = decl.get( "property", "" ).strip()
			value = decl.get( "value", "" ).strip()

			# Replace any placeholders ${var} using self.get(var)
			skip = False
			def repl( match ):
				var_name = match.group( 1 )
				value = self.sanitize_name( self.get( var_name ) )

				if value and value != "default":
					# Wrap with var() so it references a CSS variable
					return f"var(--{value})"
				else:
					nonlocal skip
					skip = True
					return ""

			# Regex: matches ${var} or ${{var}}
			value = re.sub( r"\${{\s*(\w+)\s*}}", repl, value )

			if skip:
				continue

			important = " !important" if decl.get( "important", False ) else ""

			if minify:
				css_lines.append( f"{prop}:{value}{important};" )
			else:
				css_lines.append( f"    {prop}: {value}{important};" )

		# Close CSS block
		css_lines.append( "}" if minify else "}\n\n" )

		# Join lines
		return "".join( css_lines ) if minify else "\n".join( css_lines )


	# Convert a string into a CSS-safe custom property name.
	#    Args:
	#        input (str): String to normalize
	def sanitize_name( self, input: str ) -> str:
		if not input:
			return ""

		# Normalize unicode (é → e, etc.)
		value = unicodedata.normalize( "NFKD", input )
		value = value.encode( "ascii", "ignore" ).decode( "ascii" )

		# Lowercase
		value = value.lower()

		# Replace spaces and underscores with hyphens
		value = re.sub( r"[\s_]+", "-", value )

		# Remove all invalid characters
		value = re.sub( r"[^a-z0-9\-]", "", value )

		# Collapse multiple hyphens
		value = re.sub( r"-{2,}", "-", value )

		# Trim hyphens
		value = value.strip( "-" )

		# CSS variables cannot start with a digit
		if value and value[ 0 ].isdigit():
			value = f"v-{value}"

		return value
