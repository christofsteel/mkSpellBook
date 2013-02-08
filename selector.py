#!/usr/bin/env python3

import sqlite3
import shlex
import argparse
import Dialog3

class Menu:
	def __init__(self, spellsfile):
		self.spells = set()
		con = sqlite3.connect("spells.db")
		con.row_factory = sqlite3.Row
		self.cur = con.cursor()
		self.d = Dialog3.Dialog()
		self.spellsfile = spellsfile
		try:
			f = open(spellsfile, "r")
			self.load(f.read())
			f.close()
		except IOError:
			print("Cannot open: " + spellsfile)
	
	def handleret(self, rc, nextmenu, prevmenu):
		if rc == 3:
			self.save()
		elif rc == 0:
			nextmenu()
		else:
			prevmenu()

	def askedition(self):
		erc, ech  = self.d.menu("Which Edition of D&D", 
				[("1", "D&D 3.5"), ("2", "D&D 3.0")], 
				height=40, width=90, menu_height=33,
				common="--extra-button --extra-label \"Save\"")
		if ech:
			self.edition = ech
		self.handleret(erc, self.askclass, lambda : exit(1))

	def askclass(self):
		self.cur.execute("select distinct class from levels")
		classesrows = self.cur.fetchall()
		classes = list(map(lambda t: t[0], classesrows))
		classeschoices = zip(map(str, range(len(classes)+1)[1:]),classes)
		crc, cch = self.d.menu("Which Spelllist?",
				classeschoices, height=40, width=90, menu_height=33,
				common="--extra-button --extra-label \"Save\"")
		if cch:
			self.d20class = classes[int(cch)-1]
		self.handleret(crc, self.askbook, self.askedition)

	def askbook(self):
		dnd30 = "edition = 'Oriental Adventures' or edition = 'Supplementals (3.0)' or edition = 'Forgotten Realms (3.0)'"
		dnd35 = "edition = 'Forgotten Realms (3.5)' or edition = 'Supplementals (3.5)' or edition = 'Core (3.5)' or edition = 'Eberron (3.5)'"
		self.cur.execute("select distinct book, edition from spells join levels on spells.id = levels.spell where class='" + self.d20class + "' and ("+ (dnd35 if self.edition == "1" else dnd30) + ") order by edition, book" )
		booksrows = self.cur.fetchall()
		bookslist = list(map(lambda t: t[0], booksrows))
		books = zip(map(str, range(len(booksrows)+1)[1:]), map(lambda row : row[0] + " (" + row[1] + ")" , booksrows))

		brc, bch = self.d.menu("Which Book?",
				books, height=40, width=90, menu_height=33,
				common="--extra-button --extra-label \"Save\"")
		if bch:
			self.book = bookslist[int(bch)-1]
		self.handleret(brc, self.asklevel, self.askclass)

	def asklevel(self):
		self.cur.execute("select distinct level from levels join spells on levels.spell = spells.id where class = '" + self.d20class + "' and book=\"" + self.book + "\" order by level")
		levelsrow = self.cur.fetchall()
		levels = list(map(lambda t: t[0], levelsrow))
		levelschoices = zip(map(str, range(len(levels)+1)[1:]), map(lambda lvl : "Level: " + str(lvl),levels))
		lrc, lch = self.d.menu("Select spell level",
				levelschoices, height=40, width=90, menu_height=33,
				common="--extra-button --extra-label \"Save\"")
		if lch:
			self.level = levels[int(lch)-1]
		self.handleret(lrc, self.selectspells, self.askbook)

	def selectspells(self):
		self.cur.execute("select id, name from spells join levels on spells.id = levels.spell where class='" + self.d20class + "' and book=\"" + self.book + "\" and level='" + str(self.level) + "' order by name")
		spellsrow = self.cur.fetchall()
		spells = list(map(tuple, spellsrow))
		spellschoice = map(lambda t: (str(t[0]), t[1], "on" if (str(t[0]), self.d20class) in self.spells else "off") , spells)
		src, sch = self.d.checklist("Select Spells", spellschoice,
				height=40, width=90, menu_height=33,
				common="--extra-button --extra-label \"Save\"")
		if sch:			
			shown_spells = set(map(lambda t: (str(t[0]), self.d20class), spells))
			selected_spells = set(map(lambda s: (s, self.d20class), sch.split()))
			deselected_spells = shown_spells.difference(selected_spells)
			self.spells = self.spells.difference(deselected_spells)
			self.spells = self.spells.union(selected_spells)
		self.handleret(src, self.askbook, self.asklevel)

	def load(self, spells):
		for i in range(int(len(spells.split())/2)):
			self.spells.add((spells.split()[2*i], spells.split()[2*i+1]))

	def save(self):
		f = open(self.spellsfile, "w")
		for spell in self.spells:
			f.write(spell[0] + " " + spell[1] + "\n")
		f.close()

parser = argparse.ArgumentParser()
parser.add_argument("--file", "-f", default="selection", metavar="FILE")
args = parser.parse_args()

menu = Menu(args.file)
menu.askedition()
