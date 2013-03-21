from mkSpellbook import __path__
from mkSpellbook.spells import Spells
from mkSpellbook.genlatex import Genlatex
from mkSpellbook.models import *

from PySide import QtCore, QtGui, QtUiTools

import sys
import os

class SpellsPopulateThread(QtCore.QThread):
	signal = QtCore.Signal(list)
	def __init__(self,database, parent=None):
		QtCore.QThread.__init__(self, parent)
		self.spells = Spells(database)

	def run(self):
		spells = self.spells.listSpellsWithClasslevels()
		for spell in spells:
			print(spell.spell.name)
			name = QtGui.QStandardItem(spell.spell.name)
			name.setCheckable(True)
			d20class = QtGui.QStandardItem(spell.classlevel.d20class)
			level = QtGui.QStandardItem(spell.classlevel.level)
			book = QtGui.QStandardItem(spell.spell.book)
			duration = QtGui.QStandardItem(spell.spell.duration)
			self.signal.emit([name, d20class, level, duration])
		

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
		#tab.populateSpellTable()

class SpellBookTab():
	def __init__(self, parent, spellbook, spells, app, database):
		self.tab = QtUiTools.QUiLoader().load(os.path.join(os.path.dirname(__file__), 'spellbookview.ui'), parent)
		self.spellbook = spellbook
		self.spells = spells
		self.database = database

		self.rulesets = QtGui.QStandardItemModel(self.tab.rulesetList)
		self.rulesets.itemChanged.connect(lambda param: self.updateClassOptions(param))
		self.tab.rulesetList.setModel(self.rulesets)
		for ruleset in self.spells.listRulesets():
			item = QtGui.QStandardItem(ruleset)
			item.setCheckable(True)
			self.rulesets.appendRow(item)

		self.classes = QtGui.QStandardItemModel(self.tab.classList)
		self.classes.itemChanged.connect(lambda param: self.updateBookOptions(param))
		self.tab.classList.setModel(self.classes)
		for d20class in self.spells.listClasses([]):
			item = QtGui.QStandardItem(d20class)
			item.setCheckable(True)
			self.classes.appendRow(item)

		self.books = QtGui.QStandardItemModel(self.tab.bookList)
		self.books.itemChanged.connect(lambda param: self.updateLevelOptions(param))
		self.tab.bookList.setModel(self.books)
		for book in self.spells.listBooks([], []):
			item = QtGui.QStandardItem(book[0] + "\n(" + book[1] + ")")
			item.setData(book)
			item.setCheckable(True)
			self.books.appendRow(item)

		self.levels = QtGui.QStandardItemModel(self.tab.levelList)
		self.books.itemChanged.connect(lambda param: self.updateLevelOptions(param))
		self.tab.levelList.setModel(self.levels)
		for level in self.spells.listLevels([], [], []):
			item = QtGui.QStandardItem(str(level))
			item.setCheckable(True)
			self.levels.appendRow(item)
		self.shownspells = QtGui.QStandardItemModel(self.tab.spellTable)
		self.shownspells.itemChanged.connect(lambda param: self.addToSpellbook)
		self.tab.spellTable.setModel(self.shownspells)
		self.oneSpellsPopulateThread = SpellsPopulateThread(self.database)
		self.oneSpellsPopulateThread.signal.connect(self.addSpell)
		self.oneSpellsPopulateThread.start()
	
	def addSpell(self, row):
		self.shownspells.appendRow(row)

	def updateSpellList(self, level):
		self.levelfilter = []
		i = 0
		while self.levels.item(i):
			if self.levels.item(i).checkState() and not self.tab.levelList.isRowHidden(i):
				self.levelfilter.append(int(self.levels.item(i).text()))
		spells = self.spells.listSpellsWithClasslevels(self.rulesetfilter, self.classfilter, self.bookfilter, self.levelfilter)
		i = 0

	def updateLevelOptions(self, book):
		self.bookfilter = []
		i = 0
		while self.books.item(i):
			if self.books.item(i).checkState() and not self.tab.bookList.isRowHidden(i):
				self.bookfilter.append(self.books.item(i).data())
			i += 1
		levels = self.spells.listLevels(self.rulesetfilter, self.classfilter, self.bookfilter)
		i = 0
		while self.levels.item(i):
			if not int(self.levels.item(i).text()) in levels:
				self.tab.levelList.setRowHidden(i, True)
			else:
				self.tab.levelList.setRowHidden(i, False)
			i += 1
		self.levels.sort(0)


	def updateBookOptions(self, d20class):
		self.classfilter = []
		i = 0
		while self.classes.item(i):
			if self.classes.item(i).checkState() and not self.tab.classList.isRowHidden(i):
				self.classfilter.append(self.classes.item(i).text())
			i += 1
		books = self.spells.listBooks(self.rulesetfilter, self.classfilter)
		i = 0
		while self.books.item(i):
			if not self.books.item(i).data() in books:
				self.tab.bookList.setRowHidden(i, True)
			else:
				self.tab.bookList.setRowHidden(i, False)
			i += 1
		self.updateLevelOptions(None)

	def updateClassOptions(self, ruleset):
		self.rulesetfilter = []	
		i = 0
		while self.rulesets.item(i):
			if self.rulesets.item(i).checkState() and not self.tab.rulesetList.isRowHidden(i):
				self.rulesetfilter.append(self.rulesets.item(i).text())
			i += 1
		classes = self.spells.listClasses(self.rulesetfilter)

		i = 0
		while self.classes.item(i):
			if not self.classes.item(i).text() in classes:
				self.tab.classList.setRowHidden(i, True)
			else:
				self.tab.classList.setRowHidden(i, False)
			i += 1

		self.updateBookOptions(None)

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

