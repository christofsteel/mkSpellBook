#!/usr/bin/env python3
from distutils.core import setup

files = ["templates/plain/*", "templates/fancy/*", "templates/fancybw/*", "importscripts/*"]

setup(name="mkSpellbook",
	version = "0.7",
	description = "Generates a Dungeons & Dragons 3rd Edition (D&D 3.0 and D&D 3.5) spellbook based on the spells available on dndtools.eu",
	author = "Christoph \"Hammy\" Stahl",
	author_email = "christoph.stahl@uni-dortmund.de",
	url = "https://github.com/christofsteel/mkspellbook",
	packages=['mkSpellbook'],
	package_dir={'' : 'src/'},
	scripts=['src/mkspellbook'],
	package_data={'mkSpellbook': files})
