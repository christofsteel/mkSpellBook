#!/usr/bin/env python3

import os
import subprocess
from mkSpellbook import __path__
from mkSpellbook.dialog import Dialog
from mkSpellbook.spells import Spells
from mkSpellbook.genlatex import Genlatex
from mkSpellbook.models import *

class Menu:
	def __init__(self):
		self.d = Dialog()
		self.d.height = 40
		self.d.width = 90
		self.d.menu_height = 33

	def caller(self, f):
		while True:
			f = f()
			if f == None:
				return None

	def mkSelection(self, selection):
		return zip(map(str, range(1, len(selection)+1)), selection)

class Spellselection(Menu):
	def __init__(self, spellbook, spells):
		Menu.__init__(self)
		self.spellbook = spellbook
		self.spells = spells

	def askruleset(self):
		rulesets = self.spells.listRulesets()
		if rulesets:
			rrc, rch  = self.d.menu("Select Ruleset", self.mkSelection(rulesets))
			if rch:
				self.ruleset = rulesets[int(rch)-1]
				return self.askclass
		return None

	def askclass(self):
		classes = self.spells.listClasses(self.ruleset)
		crc, cch = self.d.menu("Select Spelllist", self.mkSelection(classes))
		if cch and not crc:
			self.d20class = classes[int(cch)-1]
			return self.askbook
		return self.askruleset

	def askbook(self):
		bookstuple = self.spells.listBooks(self.ruleset, self.d20class)
		books = [book[0] + " (" + book[1] + ")" for book in bookstuple]
		brc, bch = self.d.menu("Select Book", self.mkSelection(books))
		if bch and not brc:
			self.book = bookstuple[int(bch)-1][0]
			return self.asklevel
		return self.askclass

	def asklevel(self):
		levels = self.spells.listLevels(self.ruleset, self.d20class, self.book)
		levelstrings = ["Level: " + str(lvl) for lvl in levels]
		lrc, lch = self.d.menu("Select spell level",self.mkSelection(levelstrings))
		if lch and not lrc:
			self.level = levels[int(lch)-1]
			return self.selectspells
		return self.askbook

	def selectspells(self):
		shownspells = self.spells.listSpellsWithClasslevels(self.ruleset, self.d20class, self.book, self.level)
		spellschoice = [(i, spell.spell.name, 
				"on" if spell in self.spellbook.spells else "off") for i, spell in self.mkSelection(shownspells)]
		src, sch = self.d.checklist("Select Spells", spellschoice)
		if sch and not src:
			shownSpellsOn = set([shownspells[int(sid)-1] for sid in sch.split()])
			shownSpellsOff = set(shownspells).difference(set(shownspells))
			self.spellbook.spells = list(set(self.spellbook.spells).difference(shownSpellsOff).union(shownSpellsOn))
			self.spells.session.commit()
			return None
		return self.asklevel

class MkSpellbook(Menu):
	def __init__(self, args):
		Menu.__init__(self)

		self.database = args.database
		self.spells = Spells(os.path.expanduser(args.database))

		self.spellbook = self.spells.getSpellbook(args.spellbook)
		self.spells.session.add(self.spellbook)

		self.template = "plain"

	def start(self):
		menuselection = [	("New Spellbook", self.newMenu),  
					("Select Spellbook", self.loadMenu), 
					("Delete a Spellbook", self.deleteMenu),  
					("Select Spells", self.spellMenu),
					("Clear Spells", self.clearSpells), 
					("Rename Spellbook", self.renameMenu),
					("Set an author", self.setAuthor), 
					("Set a logo", self.setLogo), 
					("Select Template", self.templateMenu), 
					("Export to pdf", self.pdflatex), 
					("Add Spells", self.addMenu)]

		mrc, mch = self.d.menu("Main Menu", self.mkSelection([c[0] for c in menuselection]))
		if mch and not mrc:
			return menuselection[int(mch)-1][1]
		return None

	def newMenu(self):
		src, spellbookname = self.d.inputbox("Name your spellbook", init="My Spellbook")
		if not src:
			spellbook = self.spells.session.query(Spellbook).filter(Spellbook.name == spellbookname).first()
			if spellbook:
				yrc, ych = self.d.yesno("A Spellbook called "+ spellbookname + " already exists. Overwrite it?")
				if not yrc:
					self.spells.session.delete(spellbook)
					self.spells.session.commit()
					self.spellbook = Spellbook(name=spellbookname)
					self.spells.session.add(self.spellbook)
					self.spells.session.commit()
				else:
					return self.newMenu
			else:
				self.spellbook = Spellbook(name=spellbookname)
				self.spells.session.add(self.spellbook)
				self.spells.session.commit()
		return self.start

	def loadMenu(self):	
		availspellbooks = self.spells.listSpellbooks()
		if availspellbooks == []:
			self.d.msgbox("No spellbooks saved")
			return self.start
		lrc, lch = self.d.menu("Select Spellbook", self.mkSelection([sb.name for sb in availspellbooks]))
		if lch:
			self.spellbook = availspellbooks[int(lch)-1]
		return self.start

	def deleteMenu(self):
		availspellbooks = self.spells.listSpellbooks()
		if availspellbooks:
			lrc, lch = self.d.menu("Deleta a Spellbook", self.mkSelection([sb.name for sb in availspellbooks]))
			if lch:
				if not availspellbooks[int(lch)-1] == self.spellbook:
					return lambda: self.askYesNoDelete(availspellbooks[int(lch)-1])
				else:
					mrc, mch = self.d.msgbox("You cannot delete your active spellbook")
		return self.start

	def askYesNoDelete(self, spellbook):
		yrc, ych = self.d.yesno("Do you really want to delete " + spellbook.name + "? It cannot be recovered.")
		if not yrc:
			self.spells.session.delete(spellbook)
		return self.start

	def spellMenu(self):
		menu = Spellselection(self.spellbook, self.spells)
		menu.caller(menu.askruleset)
		return self.start

	def clearSpells(self):
		yrc, ych = self.d.yesno("Are you sure to clear your spellbook? All unsaved data will be lost")
		if not yrc:
			self.spellbook.spells = []
			self.spells.session.commit()
		return self.start

	def renameMenu(self):
		src, spellbookname = self.d.inputbox("Rename Spellbook", init=self.spellbook.name)
		if not src:
			spellbook = self.spells.session.query(Spellbook).filter(Spellbook.name == spellbookname).first()
			if spellbook and spellbook != self.spellbook:
				yrc, ych = self.d.yesno("A Spellbook called "+ spellbookname + " already exists. Overwrite it?")
				if not yrc:
					self.spells.session.delete(spellbook)
					self.spells.session.commit()
					self.spellbook.name = spellbookname
					self.spells.session.add(self.spellbook)
					self.spells.session.commit()
				else:
					return self.saveMenu
			else:
				self.spellbook.name = spellbookname
				self.spells.session.commit()
		return self.start

	def setAuthor(self):
		arc, author = self.d.inputbox("Set an author:", init=self.spellbook.author)
		if author:
			self.spellbook.author = author
			self.spells.session.commit()
			return self.start
		return self.start

	def setLogo(self):
		lrc, logo = self.d.fselect("Select a logo for the Spellbook",  os.path.expanduser("~"))
		if not os.path.isfile(logo):
			erc, rch = self.d.msgbox("No such file: " + logo)
			return self.start
		if logo:
			with open(logo, "rb") as logofile:
				self.spellbook.logo = logofile.read()
			self.spellbook.logoext = os.path.splitext(logo)[1]
			self.spells.session.commit()
		return self.start

	def templateMenu(self):
		templates = []
		for template in os.listdir(__path__[0] + "/templates"):
			if os.path.isdir(__path__[0] + "/templates/" + template):
				templates.append((template, __path__[0] + "/templates/" + template))
		if os.path.isdir(os.path.expanduser("~/.mkspellbook/templates/")):
			for template in os.listdir(os.path.expanduser("~/.mkspellbook/templates/")):
				templates.append((template + " (User)", os.path.expanduser("~/.mkspellbook/templates/" + template)))
		if templates:
			trc, tch = self.d.menu("Templates", self.mkSelection([template[0] for template in templates]))
			if tch:
				self.template = templates[int(tch)-1]
		return self.start

	def pdflatex(self):
		orc, output = self.d.inputbox("Export pdf to", init=os.path.expanduser("~/" + self.spellbook.name + ".pdf"))
		if output and not orc:
			g = Genlatex()
			g.genlatex(self.spellbook, self.template[1], output)
			yrc, ych = self.d.yesno("Do you want to open your Spellbook?")
			if not yrc:
				vrc, viewer = self.d.inputbox("Which viewer do you want to use?", init="evince")
				if viewer and not vrc:
					subprocess.Popen([viewer, output])
		return self.start

	def addMenu(self):
		selection = [	("Run an import script", self.runimport),
				("Add a spell manually", self.addmanual)]
		arc, ach = self.d.menu("How do you want to add spells?", self.mkSelection([c[0] for c in selection]))
		if ach and not arc:
			return selection[int(ach)-1][1]
		return self.start

	def runimport(self):
		importscripts = []
		for importscript in os.listdir(__path__[0] + "/importscripts"):
			importscripts.append((importscript, __path__[0] + "/importscripts/" + importscript))
		if os.path.isdir(os.path.expanduser("~/.mkspellbook/importscripts/")):
			for importscript in os.listdir(os.path.expanduser("~/.mkspellbook/importscripts/")):
				importscripts.append((importscript + " (User)", __path__[0] + "/importscripts/" + importscript))
		irc, ich = self.d.menu("Select import script", self.mkSelection([script[0] for script in importscripts]))
		if ich and not irc:
			subprocess.call([importscripts[int(ich)-1][1], self.database], shell=True)


	def addmanual(self):
		pass
