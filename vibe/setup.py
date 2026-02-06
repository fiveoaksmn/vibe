import frappe
from vibe.controllers.theme import sync_themes, import_theme
from pathlib import Path
import json


def after_install():
	import_themes()
	sync_themes()


def after_migrate():
	import_themes()
	sync_themes()


def import_themes():
	themePath = Path().cwd().parent / "apps/vibe/vibe/themes"
	if themePath.is_dir():
		files = list( themePath.glob( "**/*.json" ) )
		for file in files:
			theme = json.loads( Path( file ).read_text() )
			import_theme( theme )
