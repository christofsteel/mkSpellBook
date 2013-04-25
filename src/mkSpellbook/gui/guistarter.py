from mkSpellbook import __path__
from mkSpellbook.spells import Spells
from mkSpellbook.genlatex import Genlatex
from mkSpellbook.models import *
from mkSpellbook.gui.SpellBookTab import *

from PySide import QtCore, QtGui, QtUiTools

import sys
import os


class MkSpellbook():
	def __init__(self, database, app):
		self.app = app
		self.mainWindow = QtUiTools.QUiLoader().load(os.path.join(os.path.dirname(__file__), 'mainWindow.ui'))
		self.database = database
		self.spells = Spells(database)
		self.tabs = []
	
	def show(self):
		self.mainWindow.show()

	def load(self, spellbookname):
		spellbook = self.spells.getSpellbook(spellbookname)
		self.openSpellbook(spellbook)
		self.spells.session.add(spellbook)
	
	def openSpellbook(self, spellbook):
		tab = SpellBookTab(self.mainWindow.SpellbookTabs, spellbook, self.spells, self.app, self.database)
		self.mainWindow.SpellbookTabs.addTab(tab.tab, spellbook.name)


def start(args):
	app = QtGui.QApplication([])
	mkSpellbook = MkSpellbook(args.database, app)
	mkSpellbook.show()
	mkSpellbook.load(args.spellbook)
	sys.exit(app.exec_())

if __name__ == "__main__":
	class Args:
		database = "/home/christoph/.mkspellbook/spells.db"
		spellbook = "My Spellbook"
	start(Args)

