from PySide import QtCore, QtGui
from mkSpellbook.spells import Spells

class SpellFilterThread(QtCore.QThread):
	hide = QtCore.Signal()
	show = QtCore.Signal()
	def __init__(self, parent=None, ruleset=None, d20class=None, book=None, level=None):
		QtCore.QThread.__init__(self, parent)
		self.spells = Spells(database)
	
	def run(self):
		spells = self.spells.listSpellsWithClasslevels()

class SpellsPopulateThread(QtCore.QThread):
	signal = QtCore.Signal(list)
	def __init__(self,database, parent=None):
		QtCore.QThread.__init__(self, parent)
		self.spells = Spells(database)

	def run(self):
		spells = self.spells.listSpellsWithClasslevels()
		for spell in spells:
			name = QtGui.QStandardItem(spell.spell.name)
			name.setData(spell.id)
			name.setCheckable(True)
			d20class = QtGui.QStandardItem(spell.classlevel.d20class)
			level = QtGui.QStandardItem(spell.classlevel.level)
			book = QtGui.QStandardItem(spell.spell.book)
			duration = QtGui.QStandardItem(spell.spell.duration)
			self.signal.emit([name, d20class, level, duration])
