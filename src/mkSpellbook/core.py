#!/usr/bin/env python3

import shlex
import shutil
import os
import subprocess
from mkSpellbook import __path__
from mkSpellbook.dialog import Dialog
from mkSpellbook.spells import Spells
from mkSpellbook.genlatex import Genlatex

class MkSpellbook:
	def __init__(self, args):
		self.spells = Spells(os.path.expanduser(args.database))
		self.d = Dialog()
		self.d.height = 40
		self.d.width = 90
		self.d.menu_height = 33
		self.spellbookfolder = os.path.expanduser("~/.mkspellbook/spellbooks")
		self.spellbook = args.spellbook
		self.selectedspells = set()
		self.author = "Sir Castalot"
		self.logo = ""
		self.template = "plain"
		self.load()

	def validFolderName(self, folder):
		return not "/" in folder

	def loadMenu(self):	
		availspellbooks = []
		for spellbook in os.listdir(self.spellbookfolder):
			if os.path.isdir(self.spellbookfolder + "/" + spellbook):
				availspellbooks.append(spellbook)
		if availspellbooks == []:
			self.d.msgbox("No spellbooks saved")
			return self.start
		lrc, lch = self.d.menu("Spellbooks", self.mkSelection(availspellbooks))
		if lch:
			return lambda: self.askYesNoLoad(availspellbooks[int(lch)-1])
		else:
			return self.start

	def askYesNoLoad(self, spellbook):
		yrc, ych = self.d.yesno("Are you sure to load " + spellbook + "? All unsaved data will be lost")
		return self.handleret(yrc, lambda: self.loader(spellbook), self.loadMenu)
	
	def loader(self, spellbook):
		self.spellbook = spellbook
		self.load()
		return self.start

	def clearSpells(self):
		yrc, ych = self.d.yesno("Are you sure to clear your spellbook? All unsaved data will be lost")
		if not yrc:
			self.selectedspells = set()
		return self.start
			
	def saveMenu(self):
		src, filename = self.d.inputbox("Name your Spellbook", init=self.spellbook)
		if not src:
			if self.validFolderName(filename):
				if os.path.isdir(self.spellbookfolder + "/" + filename):
					yrc, ych = self.d.yesno("A Spellbook called "+ filename + " already exists. Override it?")
					if not yrc:
						self.spellbook = filename
						return self.save
					else:
						return self.saveMenu
				else:
					self.spellbook = filename
					return self.save
			else:
				self.d.msgbox("Invalid Spellbook name")
				return self.saveMenu
		else:
			return self.start

	def deleteMenu(self):
		availspellbooks = [spellbook for spellbook in os.listdir(self.spellbookfolder) if os.path.isdir(self.spellbookfolder + "/" + spellbook)]
		if availspellbooks:
			lrc, lch = self.d.menu("Deleta a Spellbook", self.mkSelection(availspellbooks))
			if lch:
				return lambda: self.askYesNoDelete(availspellbooks[int(lch)-1])
		return self.start

	def askYesNoDelete(self, spellbook):
		yrc, ych = self.d.yesno("Do you really want to delete " + spellbook + "? It cannot be recovered.")
		if not yrc:
			shutil.rmtree(self.spellbookfolder + "/" + spellbook)
		return self.start


	def templateMenu(self):
		templates = []
		for template in os.listdir(__path__[0] + "/templates"):
			if os.path.isdir(__path__[0] + "/templates/" + template):
				templates.append(template)
		if templates:
			trc, tch = self.d.menu("Templates", self.mkSelection(templates))
			if tch:
				self.template = templates[int(tch)-1]
		return self.start

	def pdflatex(self):
		g = Genlatex()
		g.genlatex(self.spellbookfolder, self.spellbook, self.spells, self.selectedspells, (__path__[0] + "/templates/" + self.template + "/"), self.author, self.logo)
		return self.start

	
	def viewSpellbook(self):
		vrc, viewer = self.d.inputbox("Which viewer do you want to use?", init="evince")
		if viewer:
			subprocess.Popen([viewer, self.spellbookfolder + "/" + self.spellbook + "/" + self.spellbook + ".pdf"])
		return self.start
			
	
	def addMenu(self):
		selection = [	("Run an import script", self.runimport),
				("Add a spell manually", self.addmanual)]
		arc, ach = self.d.menu("How do you want to add spells?", self.mkSelection(c[0] for c in selection))


	def load(self):
		try:
			os.makedirs(self.spellbookfolder)
		except OSError:
			if not os.path.isdir(self.spellbookfolder):
				raise

		try:
			f = open(self.spellbookfolder + "/" + self.spellbook + "/spellselection", "r")			
			selectedspellsraw = f.read()
			f.close()

		except IOError:
			selectedspellsraw = ""
			return

		self.selectedspells = set()
		lines = selectedspellsraw.split('\n')
		self.author = lines[0]
		self.logo = lines[1]

		for line in lines[2:]:
			if line:
				self.selectedspells.add((int(line.split(' ')[0]), line.split(' ')[1]))


	def mkSelection(self, selection):
		return zip(map(str, range(1, len(selection)+1)), selection)

	def caller(self, f):
		while True:
			f = f()
		
	def start(self):
		menuselection = [	("Select Spellbook", self.loadMenu), 
					("Select Spells", self.askruleset), 
					("Clear Spells", self.clearSpells), 
					("Set an author", self.askAuthor), 
					("Set a logo", self.askLogo), 
					("Save Spellbook", self.saveMenu),  
					("Delete a Spellbook", self.deleteMenu),  
					("Select Template", self.templateMenu), 
					("PDFLatex", self.pdflatex), 
					("View Spellbook", self.viewSpellbook), 
					("Add Spells", self.addMenu)]

		mrc, mch = self.d.menu("Main Menu", self.mkSelection([c[0] for c in menuselection]))
		f = menuselection[int(mch)-1][1] if mch else id
		return self.handleret(mrc, f, lambda: exit(0))
		
	def handleret(self, rc, nextmenu, prevmenu):
		if rc == 0:
			return nextmenu
		else:
			return prevmenu

	def askruleset(self):
		rulesets = self.spells.getRulesets()
		if rulesets:
			rrc, rch  = self.d.menu("Select Ruleset", self.mkSelection(rulesets))
			if rch:
				self.ruleset = rulesets[int(rch)-1]
				return self.askclass
		return self.start

	def askclass(self):
		classes = self.spells.getClasses(self.ruleset)
		crc, cch = self.d.menu("Select Spelllist", self.mkSelection(classes))
		if cch:
			self.d20class = classes[int(cch)-1]
		return self.handleret(crc, self.askbook, self.askruleset)

	def askbook(self):
		bookstuple = self.spells.getBooks(self.ruleset, self.d20class)
		books = [book[0] + " (" + book[1] + ")" for book in bookstuple]
		brc, bch = self.d.menu("Select Book", self.mkSelection(books))
		if bch:
			self.book = bookstuple[int(bch)-1][0]
		return self.handleret(brc, self.asklevel, self.askclass)

	def asklevel(self):
		levels = self.spells.getLevels(self.ruleset, self.d20class, self.book)
		levelstrings = ["Level: " + str(lvl) for lvl in levels]
		lrc, lch = self.d.menu("Select spell level",self.mkSelection(levelstrings))
		if lch:
			self.level = levels[int(lch)-1]
		return self.handleret(lrc, self.selectspells, self.askbook)

	def selectspells(self):
		shownspells = self.spells.getSpells(self.ruleset, self.d20class, self.book, self.level)
		spellschoice = [(str(spell['id']), spell['name'], 
				"on" if (spell['id'], spell['class'])  in self.selectedspells else "off") for spell in shownspells]
		src, sch = self.d.checklist("Select Spells", spellschoice)
		if sch:			
			shownSpellsIds = set([(spell['id'], spell['class']) for spell in shownspells])
			shownSpellsOnIds = set([(int(sid), self.d20class) for sid in sch.split()])
			shownSpellsOffIds = shownSpellsIds.difference(shownSpellsOnIds)
			self.selectedspells = self.selectedspells.difference(shownSpellsOffIds)
			self.selectedspells = self.selectedspells.union(shownSpellsOnIds)
		return self.handleret(src, self.askbook, self.asklevel)

	def askAuthor(self):
		arc, author = self.d.inputbox("Set an author:", init=self.author)
		if author:
			self.author = author
			return self.start
		return self.start

	def askLogo(self):
		lrc, logo = self.d.fselect("Select a logo for the Spellbook",  os.path.expanduser("~"))
		if logo:
			self.logo = logo
			return self.start
		return self.start

	def save(self):
		try:
			os.makedirs(self.spellbookfolder + "/" + self.spellbook)
		except OSError:
			if not os.path.isdir(self.spellbookfolder):
				raise
		f = open(self.spellbookfolder + "/" + self.spellbook + "/spellselection", "w")		
		f.write(self.author + '\n')
		f.write(self.logo + '\n')
		for spell in self.selectedspells:
			f.write(str(spell[0]) + " " + spell[1] + "\n")
		f.close()

		return self.start
