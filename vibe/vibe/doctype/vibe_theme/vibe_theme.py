# Copyright (c) 2026, Five Oaks, Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder.functions import Lower
from vibe.controllers.theme import sync_themes
import re
import unicodedata


class VibeTheme( Document ):
    _COLOR_SELECTS = [
        "core_primary_text_color", "core_secondary_text_color", "core_link_color",
        "core_background_color", "core_surface_color", "core_border_color",
        "core_primary_color", "core_secondary_color", "core_success_color", "core_danger_color", "core_warning_color", "core_info_color",
        "navbar_background_color", "navbar_icon_color", "navbar_breadcrumb_color", "navbar_title_color", "navbar_breadcrumb_separator_color",
        "sidebar_background_color", "sidebar_header_background_color", "sidebar_header_title_color",
        "sidebar_header_subtitle_color", "sidebar_header_hover_background_color",
        "sidebar_header_hover_title_color", "sidebar_header_hover_subtitle_color",
        "sidebar_header_active_background_color", "sidebar_header_active_title_color",
        "sidebar_header_active_subtitle_color", "sidebar_notification_dot_color",
        "sidebar_middle_icon_color", "sidebar_middle_item_color",
        "sidebar_middle_item_suffix_color", "sidebar_middle_hover_background_color",
        "sidebar_middle_hover_icon_color", "sidebar_middle_hover_item_color",
        "sidebar_middle_hover_item_suffix_color", "sidebar_middle_active_background_color",
        "sidebar_middle_active_icon_color", "sidebar_middle_active_item_color",
        "sidebar_middle_active_item_suffix_color", "sidebar_footer_background_color", "sidebar_footer_title_color",
        "sidebar_footer_subtitle_color", "sidebar_footer_hover_background_color",
        "sidebar_footer_hover_title_color", "sidebar_footer_hover_subtitle_color"
    ]
    _OTHER_PROPS = [
        "sidebar_notification_dot_size"
    ]

    # Conversion factors to px (CSS absolute units, plus em/rem at a 16px base)
    _TO_PX = {
        "px": 1.0,
        "in": 96.0,
        "cm": 96.0 / 2.54,
        "mm": 96.0 / 25.4,
        "q": 96.0 / 101.6,
        "pt": 96.0 / 72.0,
        "pc": 16.0,
        "em": 16.0,
        "rem": 16.0,
    }
    _RELATIVE = { "%", "vw", "vh", "vmin", "vmax", "ch", "ex" }
    _PATTERN = re.compile( r"^\s*([+-]?(?:\d+\.?\d*|\.\d+))\s*([a-zA-Z%]*)\s*$" )

    def validate( self ):
        # Three default Frappe themes not allowed
        if self.theme_title.lower() in [ "light", "dark", "automatic" ]:
            frappe.throw( f"Theme title '{self.theme_title}' is reserved." )

        # No special characters in title
        if not re.fullmatch( r"[A-Za-z0-9\- ]+", self.theme_title ):
            frappe.throw( _( "The title can only contain letters, numbers, spaces, and dashes." ) )

        # Make sure the title wasn't used already
        vibeTheme = frappe.qb.DocType( "Vibe Theme" )
        qb = (
            frappe.qb.from_( vibeTheme )
            .select( vibeTheme.name )
            .where( Lower( vibeTheme.theme_title ) == self.theme_title.lower() )
        )
        if not self.is_new():
            qb = qb.where( vibeTheme.name != self.name )
        if len( qb.run() ) > 0:
            frappe.throw( _( "A theme with this title already exists." ) )

        # Notification dot size
        if self.sidebar_notification_dot_size:
            if self.sidebar_notification_dot_size < 0:
                self.sidebar_notification_dot_size = 0
            elif self.sidebar_notification_dot_size > 10:
                self.sidebar_notification_dot_size = 10


    def on_update( self ):
        sync_themes()


    # Component rules shared by every theme, as ( selectors, declarations ).
    #    ${{fieldname}} placeholders become var(--vibe-<fieldname>), which each theme defines in its :root block.
    #    A declaration is only emitted for the themes that set every field it references, so an unset
    #    field still falls back to Frappe's default instead of blanking the property.
    _RULES = [
            ### CORE

        # Page Background
        ( [ "body", ".std-form-layout > .form-layout > .form-page", ".desktop-container", ".grid-footer" ], [ { "property": "background-color", "value": "${{core_background_color}}", "important": True } ] ),

        # Links
        ( [ "a" ], [ { "property": "color", "value": "${{core_link_color}}" } ] ),

            ### NAVBAR

            # Navbar Background
        ( [ ".page-head-content", ".navbar" ], [ { "property": "background-color", "value": "${{navbar_background_color}}", "important": True } ] ),

            # Navbar Icon
        ( [ ".navbar-breadcrumbs > li > a > svg", ".sidebar-toggle-icon svg", ".sidebar-toggle-btn svg" ], [ { "property": "color", "value": "${{navbar_icon_color}}", "important": True }, { "property": "stroke", "value": "${{navbar_icon_color}}" } ] ),

            # Navbar Toggle Icon Hovered
        ( [ ".sidebar-toggle-icon:hover .es-icon" ], [ { "property": "fill", "value": "${{navbar_icon_color}}", "important": True }, { "property": "stroke", "value": "${{navbar_icon_color}}" } ] ),

            # Navbar Breadcrumbs
        ( [ ".navbar-breadcrumbs > li:not(.disabled) > a", ".navbar-breadcrumbs li.ellipsis" ], [ { "property": "color", "value": "${{navbar_breadcrumb_color}}" } ] ),

            # Navbar Page Title
        ( [ ".navbar-breadcrumbs > li.disabled > a", ".navbar-breadcrumbs li:last-child > a" ], [ { "property": "color", "value": "${{navbar_title_color}}", "important": True } ] ),

            # Navbar Breadcrumb Separator
        ( [ ".navbar-breadcrumbs a::before" ], [ { "property": "color", "value": "${{navbar_breadcrumb_separator_color}}" } ] ),

            ### SIDEBAR

            # Sidebar Background
        ( [ ".body-sidebar" ], [ { "property": "background-color", "value": "${{sidebar_background_color}}", "important": True } ] ),

        # Sidebar Header: Background / Title / Subtitle
        ( [ ".sidebar-header" ], [ { "property": "background-color", "value": "${{sidebar_header_background_color}}" } ] ),
        ( [ ".sidebar-header .header-title" ], [ { "property": "color", "value": "${{sidebar_header_title_color}}" } ] ),
        ( [ ".sidebar-header .header-subtitle" ], [ { "property": "color", "value": "${{sidebar_header_subtitle_color}}" } ] ),

        # Sidebar Header: Hover
        ( [ ".sidebar-header.hover" ], [ { "property": "background-color", "value": "${{sidebar_header_hover_background_color}}", "important": True }, { "property": "border-radius", "value": "8px" } ] ),
        ( [ ".sidebar-header.hover .header-title" ], [ { "property": "color", "value": "${{sidebar_header_hover_title_color}}" } ] ),
        ( [ ".sidebar-header.hover .header-subtitle" ], [ { "property": "color", "value": "${{sidebar_header_hover_subtitle_color}}" } ] ),

        # Sidebar Header: Active
        ( [ ".sidebar-header.active-sidebar" ], [ { "property": "background-color", "value": "${{sidebar_header_active_background_color}}", "important": True }, { "property": "border-radius", "value": "8px" } ] ),
        ( [ ".sidebar-header.active-sidebar .header-title" ], [ { "property": "color", "value": "${{sidebar_header_active_title_color}}" } ] ),
        ( [ ".sidebar-header.active-sidebar .header-subtitle" ], [ { "property": "color", "value": "${{sidebar_header_active_subtitle_color}}" } ] ),

        # Sidebar Middle: Icons / Item / Item Suffix
        ( [ ".sidebar-item-icon svg:not(.sidebar-item-icon > .header-logo svg)", ".collapse-sidebar-link svg" ], [ { "property": "color", "value": "${{sidebar_middle_icon_color}}" }, { "property": "stroke", "value": "${{sidebar_middle_icon_color}}" } ] ),
        ( [ ".standard-sidebar-item:not(.active-sidebar) .sidebar-item-label" ], [ { "property": "color", "value": "${{sidebar_middle_item_color}}" } ] ),
        ( [ ".sidebar-item-suffix .keyboard-shortcut", ".collapse-sidebar-link" ], [ { "property": "color", "value": "${{sidebar_middle_item_suffix_color}}" } ] ),

        # Sidebar Middle: Hover
        ( [ ".body-sidebar .standard-sidebar-item:not(.active-sidebar):has(a:not(.section-break)):hover" ], [ { "property": "background-color", "value": "${{sidebar_middle_hover_background_color}}" } ] ),
        ( [ ".standard-sidebar-item:not(.active-sidebar):hover a svg", ".collapse-sidebar-link:hover svg" ], [ { "property": "color", "value": "${{sidebar_middle_hover_icon_color}}" }, { "property": "stroke", "value": "${{sidebar_middle_hover_icon_color}}" } ] ),
        ( [ ".standard-sidebar-item:not(.active-sidebar):hover a .sidebar-item-label" ], [ { "property": "color", "value": "${{sidebar_middle_hover_item_color}}" } ] ),
        ( [ ".standard-sidebar-item:not(.active-sidebar):hover a .sidebar-item-suffix .keyboard-shortcut", ".collapse-sidebar-link:hover" ], [ { "property": "color", "value": "${{sidebar_middle_hover_item_suffix_color}}" } ] ),

        # Sidebar Middle: Active
        ( [ ".active-sidebar" ], [ { "property": "background-color", "value": "${{sidebar_middle_active_background_color}}" } ] ),
        ( [ ".active-sidebar svg" ], [ { "property": "color", "value": "${{sidebar_middle_active_icon_color}}", "important": True }, { "property": "stroke", "value": "${{sidebar_middle_active_icon_color}}", "important": True } ] ),
        ( [ ".active-sidebar .sidebar-item-label" ], [ { "property": "color", "value": "${{sidebar_middle_active_item_color}}" } ] ),
        ( [ ".active-sidebar .sidebar-item-suffix" ], [ { "property": "color", "value": "${{sidebar_middle_active_item_suffix_color}}" } ] ),

        # Sidebar Footer: Background / Title (username) / Subtitle (email)
        ( [ ".dropdown-navbar-user" ], [ { "property": "background-color", "value": "${{sidebar_footer_background_color}}" }, { "property": "border-radius", "value": "8px", "important": True } ] ),
        ( [ ".avatar-name-email" ], [ { "property": "color", "value": "${{sidebar_footer_title_color}}" } ] ),
        ( [ ".standard-sidebar-item .keyboard-shortcut" ], [ { "property": "color", "value": "${{sidebar_footer_subtitle_color}}" } ] ),

        # Sidebar Footer: Hover
        ( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user:hover" ], [ { "property": "background-color", "value": "${{sidebar_footer_hover_background_color}}" }, { "property": "border-radius", "value": "8px", "important": True } ] ),
        ( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user:hover .avatar-name-email" ], [ { "property": "color", "value": "${{sidebar_footer_hover_title_color}}" } ] ),
        ( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user:hover .avatar-name-email > .text-secondary" ], [ { "property": "color", "value": "${{sidebar_footer_hover_subtitle_color}}" } ] ),

            # Sidebar Footer: Fix Padding & Borders
        ( [ ".body-sidebar-container.expanded .body-sidebar .dropdown-navbar-user" ], [
                    { "property": "border-radius", "value": "8px", "important": True },
                    { "property": "padding-left", "value": "8px" },
                    { "property": "padding-right", "value": "8px" }
        ] ),

        ### NOTIFICATIONS

        ( [ ".indicator.blue::before", ".indicator.blue::after" ], [ { "property": "background", "value": "${{sidebar_notification_dot_color}}", "important": True } ] ),
        ( [ ".sidebar-notification .sidebar-item-icon.indicator::before", ".desktop-notification-icon.indicator::before" ], [ { "property": "width", "value": "${{sidebar_notification_dot_size}}" }, { "property": "height", "value": "${{sidebar_notification_dot_size}}" } ] ),
    ]
    _PLACEHOLDER = re.compile( r"\${{\s*(\w+)\s*}}" )


    # Generate this theme's CSS
    #    Args:
    #        minify (bool): If True, minify CSS output; else pretty-print.
    #        preview_only (bool): If True, only output the .theme-grid preview rules.
    #        include_rules (bool): If True, also output the component rules scoped to this theme alone.
    #            stylesheet.css() passes False and calls generate_rules() once for every theme instead.
    def get_css( self, minify = True, preview_only = False, include_rules = True ):
        css = ""
        if not preview_only:
            css = self.generate_palette( minify = minify, additional = self.get_core_variables(), component_variables = self.get_component_variables() )
            if include_rules:
                css += VibeTheme.generate_rules( [ self ], minify = minify )

        ### Theme Preview

        css += self.generate_selector( [ ".theme-grid div[data-theme='" + self.theme_title.lower() + "'] .background" ], [ { "property": "background-color", "value": "${{core_background_color}}", "important": True } ], minify = minify, theme_selector = False, use_hex = True )
        if self.navbar_background_color is not None:
            css += self.generate_selector( [ ".theme-grid div[data-theme='" + self.theme_title.lower() + "'] .navbar" ], [ { "property": "background-color", "value": "${{navbar_background_color}}", "important": True } ], minify = minify, theme_selector = False, use_hex = True )
        else:
            css += self.generate_selector( [ ".theme-grid div[data-theme='" + self.theme_title.lower() + "'] .navbar" ], [ { "property": "background-color", "value": "#ededed", "important": True } ], minify = minify, theme_selector = False, use_hex = True )
        css += self.generate_selector( [ ".theme-grid div[data-theme='" + self.theme_title.lower() + "'] .toolbar > .text" ], [ { "property": "background-color", "value": "${{sidebar_background_color}}", "important": True } ], minify = minify, theme_selector = False, use_hex = True )

        return css


    # Generate the component rules once for a set of themes
    #    Each declaration is scoped to only the themes that set its field(s), e.g.
    #        :where(:root):is([data-theme="ash"],[data-theme="desert"]) .navbar { background-color: var(--vibe-navbar-background-color) !important; }
    #    :where(:root) limits the match to <html> (so a .theme-grid preview div never activates it) and adds no specificity,
    #    so each selector has the same specificity as the old [data-theme="x"] .navbar form.
    #    Args:
    #        themes (list[VibeTheme]): Themes to include.
    #        minify (bool): If True, minify CSS output; else pretty-print.
    @staticmethod
    def generate_rules( themes, minify = True ):
        theme_values = [ ( theme.theme_title.lower(), theme.get_component_variables() ) for theme in themes ]

        css = ""
        for selectors, declarations in VibeTheme._RULES:
            # Group declarations by the set of themes they apply to (usually one group per rule)
            groups = { }
            for decl in declarations:
                fields = VibeTheme._PLACEHOLDER.findall( decl[ "value" ] )
                codes = tuple( code for code, values in theme_values if all( field in values for field in fields ) )
                if not codes:
                    continue

                value = VibeTheme._PLACEHOLDER.sub( lambda m: f"var({VibeTheme.variable_name( m.group( 1 ) )})", decl[ "value" ] )
                important = " !important" if decl.get( "important", False ) else ""
                groups.setdefault( codes, [ ] ).append( f"{decl[ 'property' ]}:{value}{important};" if minify else f"    {decl[ 'property' ]}: {value}{important};" )

            for codes, lines in groups.items():
                scope = VibeTheme.theme_scope( codes )
                selector_str = ( "," if minify else ", " ).join( f"{scope} {s}" for s in selectors )
                if minify:
                    css += f"{selector_str}{{{''.join( lines )}}}"
                else:
                    css += f"{selector_str} {{\n" + "\n".join( lines ) + "\n}\n\n"

        return css


    # Selector that matches <html> when any of the given themes is active
    #    Args:
    #        codes (list[str]): Lowercased theme titles.
    @staticmethod
    def theme_scope( codes ):
        attrs = [ f'[data-theme="{code}"]' for code in codes ]
        return ":where(:root)" + ( attrs[ 0 ] if len( attrs ) == 1 else f":is({','.join( attrs )})" )


    # CSS custom property name for a component field, e.g. navbar_background_color -> --vibe-navbar-background-color
    @staticmethod
    def variable_name( fieldname ):
        return "--vibe-" + fieldname.replace( "_", "-" )


    # Fields referenced by _RULES, in order
    @classmethod
    def rule_fields( cls ):
        fields = [ ]
        for _, declarations in cls._RULES:
            for decl in declarations:
                for field in cls._PLACEHOLDER.findall( decl[ "value" ] ):
                    if field not in fields:
                        fields.append( field )
        return fields


    # Values for this theme's --vibe-* variables. Fields left unset are omitted.
    def get_component_variables( self ):
        values = { }
        for fieldname in self.rule_fields():
            if fieldname in self._OTHER_PROPS:
                size = self.get( fieldname )
                if size:
                    values[ fieldname ] = f"{float( size ):g}px"
            else:
                # Resolve the palette name straight to its hex code; unknown or "default" names are omitted
                color = self.get_palette().get( self.sanitize_name( self.get( fieldname ) ) )
                if color:
                    values[ fieldname ] = color
        return values


    # Palette as { sanitized color name: color value }
    def get_palette( self ):
        return { self.sanitize_name( row.color_name ): row.color.strip() for row in self.palette if row.color_name and row.color }


    # Frappe's own variables that this theme overrides
    def get_core_variables( self ):
        variables = []
        self.set_variable( variables, [ "text-color" ], "core_primary_text_color" )
        self.set_variable( variables, [ "text-muted" ], "core_secondary_text_color" )
        self.set_variable( variables, [ "text-info", "alert-text-info" ], "core_info_color" )
        self.set_variable( variables, [ "text-success", "alert-text-success" ], "core_success_color" )
        self.set_variable( variables, [ "text-warning", "alert-text-warning" ], "core_warning_color" )
        self.set_variable( variables, [ "text-danger", "alert-text-danger" ], "core_danger_color" )
        self.set_variable( variables, [ "primary", "primary-color" ], "core_primary_color" )
        return variables


    # Generate this theme's :root[data-theme="..."] variable block (hex values only, no palette variables)
    #    Args:
    #        minify (bool): If True, minify CSS output; else pretty-print.
    #        additional (list): Frappe variables to override (see get_core_variables).
    #        component_variables (dict): --vibe-* variables (see get_component_variables).
    def generate_palette( self, minify=True, additional = None, component_variables = None ):
        lines = [ ]

        # Use quotes for data-theme to be safe
        theme_selector = f'[data-theme="{self.theme_title.lower()}"]'
        palette = self.get_palette()

        # Opening bracket
        if minify:
            lines.append( f":root{theme_selector}{{" )
        else:
            lines.append( f":root{theme_selector} {{" )

        # Additional color variables
        if additional is not None:
            for row in additional:
                var_name = "--" + row[ "color_name" ]
                if row[ "color" ] in palette:
                    var_value = palette[ row[ "color" ] ]
                    if minify:
                        lines.append( f"{var_name}:{var_value} !important;" )
                    else:
                        lines.append( f"    {var_name}: {var_value} !important;" )

        # Component variables used by the shared rules
        if component_variables:
            for fieldname, var_value in component_variables.items():
                var_name = self.variable_name( fieldname )
                if minify:
                    lines.append( f"{var_name}:{var_value};" )
                else:
                    lines.append( f"    {var_name}: {var_value};" )

        lines.append( "}" if minify else "}\n\n" )

        # Join lines
        css = "".join( lines ) if minify else "\n".join( lines )
        return css


    # Append variable
    #    Args:
    #        variables (list): Reference to array containing variables
    #        name (stR): Name for CSS variable
    #        fieldname (str): Name of corresponding doc field
    def set_variable( self, variables, names, fieldname ):
        if self.get( fieldname ):
            value = self.sanitize_name( self.get( fieldname ) )
            if isinstance( names, str ):
                variables.append( { "color_name": names, "color": value } )
            else:
                for name in names:
                    variables.append( { "color_name": name, "color": value } )


    # Generate a CSS string from selectors and declarations, replacing variables.
    #    Args:
    #        selectors (list[str]): List of CSS selectors.
    #        declarations (list[dict]): List of {"property": str, "value": str}.
    #        minify (bool): If True, minify CSS output; else pretty-print.
    #        theme_selector (bool): If True, prepend the theme selector to every selector.
    #        use_hex (bool): If True, use HEX color codes instead of variable names.
    def generate_selector( self, selectors: list[str], declarations: list[dict], minify: bool = True, theme_selector: bool = True, use_hex: bool = False ) -> str:
        if not selectors or not declarations:
            return ""

        # Prepend the theme selector to every selector
        if theme_selector:
            theme_code = self.theme_title.lower()
            theme_selector = f'[data-theme="{theme_code}"]'
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
                if use_hex:
                    value = self.get_color_hex( self.get( var_name ) )
                    if value:
                        return value
                else:
                    value = self.sanitize_name( self.get( var_name ) )
                    if value and value != "default":
                        # Wrap with var() so it references a CSS variable
                        return f"var(--{value})"

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


    # Get the color HEX code from the palette name
    #    Args:
    #        color_name (str): The name of the color to retrieve the HEX code for.
    def get_color_hex( self, color_name ):
        for row in self.palette:
            if row.color_name == color_name:
                return row.color

        return None


    # Provide JSON
    @frappe.whitelist()
    def export_theme( self ):
        theme = { "name": self.name, "description": self.description, "palette": [] }

        for row in self.palette:
            theme[ "palette" ].append( { "name": row.color_name, "color": row.color } )

        for select in self._COLOR_SELECTS:
            group, rest = select.split( "_", 1 )  # split only on first underscore

            # Get the value from the document (works for Frappe DocTypes)
            value = self.get( select )

            # Ensure group exists
            theme.setdefault( group, { } )

            # Store
            theme[ group ][ rest ] = value

        for select in self._OTHER_PROPS:
            group, rest = select.split( "_", 1 )  # split only on first underscore

            # Get the value from the document (works for Frappe DocTypes)
            value = self.get( select )

            # Ensure group exists
            theme.setdefault( group, { } )

            # Store
            theme[ group ][ rest ] = value

        return theme


    def clean_css_size( self, value, min_value = None, max_value = None, units = None, precision = 4 ):
        """
        Validate and normalize a CSS width/height value.

        value:      "100px", "1.5 rem", "50%", 200 (bare numbers are treated as px)
        min_value:  clamp floor, e.g. "10px" or 10 (bare numbers use the output units)
        max_value:  clamp ceiling, same rules as min_value
        units:      convert the result to these units, e.g. "px", "rem"

        Returns a string like "120px". Raises ValueError on invalid input.
        """
        number, unit = self._parse( value )
        out_unit = units.lower() if units else unit
        number = self._convert( number, unit, out_unit )

        if min_value is not None:
            min_number, min_unit = self._parse( min_value, out_unit )
            number = max( number, self._convert( min_number, min_unit, out_unit ) )
        if max_value is not None:
            max_number, max_unit = self._parse( max_value, out_unit )
            number = min( number, self._convert( max_number, max_unit, out_unit ) )

        number = round( number, precision )
        text = f"{number:.{precision}f}".rstrip( "0" ).rstrip( "." )
        if text in ("-0", ""):
            text = "0"
        return f"{text}{out_unit}"


    def _parse( self, value, default_unit = "px" ):
        if isinstance( value, (int, float) ):
            return float( value ), default_unit
        match = self._PATTERN.match( str( value ) )
        if not match:
            raise ValueError( f"Invalid CSS size: {value!r}" )
        number, unit = match.groups()
        unit = unit.lower() or default_unit
        if unit not in self._TO_PX and unit not in self._RELATIVE:
            raise ValueError( f"Unknown CSS unit: {unit!r}" )
        return float( number ), unit


    def _convert( self, number, from_unit, to_unit ):
        if from_unit == to_unit:
            return number
        if from_unit in self._TO_PX and to_unit in self._TO_PX:
            return number * self._TO_PX[ from_unit ] / self._TO_PX[ to_unit ]
        raise ValueError( f"Cannot convert {from_unit} to {to_unit}" )
