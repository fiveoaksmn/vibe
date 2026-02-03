# Copyright (c) 2026, Five Oaks, Inc and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime
import time


class VibeMessage( Document ):
	def validate( self ):
		if self.status == "Queued":
			self.send_message()


	@frappe.whitelist()
	def send_message( self ):
		if self.message_type == "Broadcast":
			frappe.publish_realtime( "vibe_message", message = { "title": self.title, "message": self.message, "indicator": self.indicator_color.lower() or "blue" } )
			self.status = "Sent"
			self.message_sent = now_datetime()
			self.save()


@frappe.whitelist()
def send_test_message( **args ):
	args = frappe._dict( args )

	# Check permission
	if not frappe.has_permission( "Vibe Message", "write" ):
		frappe.throw( _( "Permission Denied" ) )

	# Check required fields
	if "message" not in args or not args.message:
		frappe.throw( _( "One or more arguments are missing" ) )

	# Kick off background task so that the API request isn't hung up
	frappe.enqueue(
		send_test_message_worker,
		timeout = 3000,
		message = args.message,
		user = frappe.session.user
	)


def send_test_message_worker( message, user ):
	# Give slight pause
	time.sleep( 5 )

	# Send the message
	frappe.publish_realtime( "vibe_message_test", user = user, message = { "message": message } )
