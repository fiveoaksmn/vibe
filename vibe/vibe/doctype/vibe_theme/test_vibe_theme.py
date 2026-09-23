# Copyright (c) 2026, Five Oaks, Inc and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class IntegrationTestVibeTheme(IntegrationTestCase):
    def test_size( self ):
        doc = frappe.new_doc( "Vibe Theme" )
        self.assertEqual( "100px", doc.clean_css_size( "100 px" ) )
        self.assertEqual( "24px", doc.clean_css_size( " 1.5 REM ", units = "px" ) )
        self.assertEqual( "10px", doc.clean_css_size( "5px", min_value = 10 ) )
        self.assertEqual( "800px", doc.clean_css_size( "900px", max_value = "50rem" ) )
        self.assertEqual( "5.08cm", doc.clean_css_size( "2in", units = "cm" ) )
        self.assertEqual( "40%", doc.clean_css_size( "50 %", max_value = 40 ) )
        self.assertEqual( "1.5rem", doc.clean_css_size( "24px", units = "rem" ) )
        try:
            doc.clean_css_size( "50%", units = "px" )
            self.fail( "ValueError should have been thrown" )
        except ValueError:
            pass
