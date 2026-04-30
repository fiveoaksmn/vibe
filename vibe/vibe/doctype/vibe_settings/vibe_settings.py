# Copyright (c) 2026, Five Oaks, Inc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class VibeSettings( Document ):
    def validate( self ):
        try:
            import rcssmin
            self.custom_css_minified = rcssmin.cssmin( self.custom_css )
        except ImportError:
            pass
