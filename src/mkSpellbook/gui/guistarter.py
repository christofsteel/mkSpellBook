from mkSpellbook import __path__
from mkSpellbook.spells import Spells
from mkSpellbook.genlatex import Genlatex
from mkSpellbook.models import *

from PySide import QtCore, QtGui, QtUiTools

import sys
import os

class MkSpellbook():
	def __init__(self, args, app):
		self.app = app
		self.mainWindow = QtUiTools.QUiLoader().load(os.path.join(os.path.dirname(__file__), 'mainWindow.ui'))

		self.spells = Spells(args.database)
		self.tabs = []
		spellbook = self.spells.getSpellbook(args.spellbook)
		self.openSpellbook(spellbook)
		self.spells.session.add(spellbook)
	
	def show(self):
		self.mainWindow.show()
	
	def openSpellbook(self, spellbook):
		tab = SpellBookTab(self.mainWindow.SpellbookTabs, spellbook, self.spells, self.app)
		self.mainWindow.SpellbookTabs.addTab(tab.tab, spellbook.name)

class SpellBookTab():
	def __init__(self, parent, spellbook, spells, app):
		self.tab = QtUiTools.QUiLoader().load(os.path.join(os.path.dirname(__file__), 'spellbookview.ui'), parent)
		self.spellbook = spellbook
		self.spells = spells

		self.rulesets = QtGui.QStandardItemModel(self.tab.rulesetList)
		self.rulesets.itemChanged.connect(lambda param: self.updateClassOptions(param))
		self.tab.rulesetList.setModel(self.rulesets)

		self.classes = QtGui.QStandardItemModel(self.tab.classList)
		self.classes.itemChanged.connect(lambda param: self.updateBookOptions(param))
		self.tab.classList.setModel(self.classes)

		self.books = QtGui.QStandardItemModel(self.tab.bookList)
		self.books.itemChanged.connect(lambda param: self.updateLevelOptions(param))
		self.tab.bookList.setModel(self.books)

		self.levels = QtGui.QStandardItemModel(self.tab.levelList)
		#self.books.itemChanged.connect(lambda param: self.updateLevelOptions(param))
		self.tab.levelList.setModel(self.levels)

		self.updateClassOptions(None)

		for ruleset in self.spells.listRulesets():
			item = QtGui.QStandardItem(ruleset)
			item.setCheckable(True)
			self.rulesets.appendRow(item)

	def updateLevelOptions(self, book):
		self.bookfilter = []
		i = 0
		while self.books.item(i):
			if self.books.item(i).checkState():
				self.bookfilter.append(self.books.item(i).data())
			i += 1
		levels = self.spells.listLevels(self.rulesetfilter, self.classfilter, self.bookfilter)
		i = 0
		while self.levels.item(i):
			if not self.levels.item(i).text() in levels:
				self.levels.takeItem(i)
				self.levels.removeRow(i)
				i -= 1
			else:
				levels.remove(self.levels.item(i).text())
			i += 1
		for level in levels:
			item = QtGui.QStandardItem(str(level))
			item.setCheckable(True)
			self.levels.appendRow(item)
		self.levels.sort(0)


	def updateBookOptions(self, d20class):
		self.classfilter = []
		i = 0
		while self.classes.item(i):
			if self.classes.item(i).checkState():
				self.classfilter.append(self.classes.item(i).text())
			i += 1
		books = self.spells.listBooks(self.rulesetfilter, self.classfilter)
		i = 0
		while self.books.item(i):
			if not self.books.item(i).data() in books:
				self.books.takeItem(i)
				self.books.removeRow(i)
				i -= 1
			else:
				books.remove(self.books.item(i).data())
			i += 1
		for book in books:
			item = QtGui.QStandardItem(book.book + " (" + book.edition + ")")
			item.setData(book)
			item.setCheckable(True)
			self.books.appendRow(item)
		self.books.sort(0)
		self.updateLevelOptions(None)

	def updateClassOptions(self, ruleset):
		self.rulesetfilter = []	
		i = 0
		while self.rulesets.item(i):
			if self.rulesets.item(i).checkState():
				self.rulesetfilter.append(self.rulesets.item(i).text())
			i += 1
		classes = self.spells.listClasses(self.rulesetfilter)
		i = 0
		while self.classes.item(i):
			if not self.classes.item(i).text() in classes:
				self.classes.takeItem(i)
				self.classes.removeRow(i)
				i -= 1
			else:
				classes.remove(self.classes.item(i).text())
			i += 1

		for d20class in classes:
			item = QtGui.QStandardItem(d20class)
			item.setCheckable(True)
			self.classes.appendRow(item)
		self.classes.sort(0)
		self.updateBookOptions(None)

def start(args):
	app = QtGui.QApplication([])
	mkSpellbook = MkSpellbook(args, app)
	mkSpellbook.show()
	sys.exit(app.exec_())

