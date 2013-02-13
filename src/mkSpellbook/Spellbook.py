#!/usr/bin/env python3
import sqlite3

class Spells:
	def __init__(self, dbname):
		con = sqlite3.connect(dbname)
		con.row_factory = sqlite3.Row
		self.cur = con.cursor()

	def makefilter(self, ruleset=None, d20class=None, book=None, level=None, id=None):
		 spellfilter = []
		 if ruleset:
			 spellfilter.append("ruleset = '" + ruleset + "'")
		 if d20class:
			 spellfilter.append("class = '" + d20class + "'")
		 if book:
			 spellfilter.append("book = \"" + book + "\"")
		 if level != None:
			 spellfilter.append("level = '" + str(level) + "'")
		 if id != None:
			 spellfilter.append("id = '" + str(id) + "'")
		 if spellfilter:
			 return " WHERE " + " AND ".join(spellfilter)
		 else:
			 return ""

	def getRulesets(self):
		self.cur.execute("SELECT DISTINCT ruleset FROM spells")
		return list(map(lambda row: row[0], self.cur.fetchall()))

	def getClasses(self, ruleset=None):
		self.cur.execute("SELECT DISTINCT class FROM spells JOIN levels ON spells.id = levels.spell" + self.makefilter(ruleset))
		return [row[0] for row in self.cur.fetchall()]
#        list(map(lambda row: row[0], self.cur.fetchall()))

	def getBooks(self, ruleset=None, d20class=None):
		self.cur.execute("SELECT DISTINCT book, edition FROM spells JOIN levels ON spells.id = levels.spell" + self.makefilter(ruleset, d20class) + " ORDER BY edition, book")
		return [(row[0], row[1]) for row in self.cur.fetchall()]
#        list(map(lambda row: tuple(row[0], row[1]), self.cur.fetchall()))


	def getLevels(self, ruleset=None, d20class=None, book=None):
		self.cur.execute("SELECT DISTINCT level FROM spells JOIN levels ON spells.id = levels.spell" + self.makefilter(ruleset, d20class, book) + " ORDER BY level")
		return [row[0] for row in self.cur.fetchall()]
#        list(map(lambda row: row[0], self.cur.fetchall()))

	def getSpells(self, ruleset=None, d20class=None, book=None, level=None, id=None):
		spells = []    
		self.cur.execute("SELECT DISTINCT * FROM spells JOIN levels ON spells.id = levels.spell" + self.makefilter(ruleset, d20class, book, level, id) + " ORDER BY level, name")
		spellrows = self.cur.fetchall()
		for spell in spellrows:
			dictspell = dict(spell)
			self.cur.execute("SELECT DISTINCT * FROM descriptors WHERE spell = '" + str(spell['id']) + "'")
			descrow = self.cur.fetchall()
			dictspell['descriptor'] = []
			for descriptor in descrow:
				dictspell['descriptor'].append(descriptor)
			spells.append(dictspell)
		return spells

	def addSpell(self, spell):
		self.cur.execute("select count(id) from spells")
		spell['id'] = int(cur.fetchall()[0][0])+1
		for k in ["id", "ruleset",  "book", "edition","school", "subschool", "verbal", "somatic", "material", "arcanefocus", "divinefocus", "xpcost"    , "castingtime", "target", "duration", "savingthrow", "spellres", "spelltext"]:
			if spell[k]:
				keys = keys + "," + k
				values = values + "," + "\""+ str(spell[k]) + "\""		
				query = "INSERT INTO spells (" + keys + ") VALUES ("+values+");"
				self.cur.execute(query)

		for k, v in spell['levels'].items():
			levelquery = "INSERT INTO levels (spell, class, level) VALUES (\"" + str(spell['id']) + "\", \"" + k + "\", \"" + str(v) +"\");"
			cur.execute(levelquery)

		if 'descriptors' in spell:
			for descriptor in spell['descriptors']:
				descquery = "INSERT INTO descriptors (spell, descriptor) VALUES (\"" + str(spell['id']) + "\", \"" + descriptor + "\");"
				cur.execute(descquery)
		con.commit()


	'''class Spell:
		def __init__(self, sqlrow=None, ruleset=None, link=None, source=None, name=None, book=None, edition=None, school=None, subschool=None, verbal=None, somatic=None, material=None, arcanefocus=None, divinefocus=None, xpcost=None, castingtime=None, spellrange=None, area=None, target=None, duration=None, savingthrow=None, spellres=None, spelltext=None):
			self.spellprop = dict()
			if sqlrow:
				self.spellprop = dict(sqlrow)
				self.spellprop['ruleset'] = ruleset
				self.spellprop['link'] = link
				self.spellprop['source'] = source
				self.spellprop['book'] = book
				self.spellprop['edition'] = edition
				self.spellprop['school'] = school
				self.spellprop['subschool'] = subschool
				self.spellprop['verbal'] = verbal
				self.spellprop['material'] = material
				self.spellprop['arcanefocus'] = arcanefocus
				self.spellprop['divinefocus'] = divinefocus
				self.spellprop['xpcost'] = xpcost
				self.spellprop['castingtime'] = castingtime
				self.spellprop['area'] = area
				self.spellprop['target'] = target
				self.spellprop['duration'] = duration
				self.spellprop['savingthrow'] = savingthrow
				self.spellprop['spellres'] = spellres
				self.spellprop['spelltext'] = spelltext



				def toDict(self):
					s = dict()
					if self.ruleset:
					s['ruleset'] = self.ruleset
					if self.link:
					s['link'] = self.link
					if self.source:
					s['source'] = self.source
					if self.book:
					s['book'] = self.book
					if self.edition:
					s['edition'] = self.edition
					if self.school:
					s['school'] = self.school
					if self.subschool:
					s['subschool'] = self.subschool
					if self.verbal:
					s['verbal'] = self.verbal
					if self.material:
					s['material'] = self.material
					if selg.arcanefocus:
					s['arcanefocus'] = self.arcanefocus
					if self.divinefocus:
					s['divinefocus'] = self.divinefocus
					if self.xpcost:
					s['xpcost'] = self.xpcost
					if self.castingtime:
					s['castingtime'] = self.castingtime
					if self.area:
					s['area'] = self.area
					if self.target:
					s['target'] = self.target
					if self.duration:
					s['duration'] = self.duration
					if self.savingthrow:
					s['savingthrow'] = self.savingthrow
					if self.spellres:
					s['spellres'] = self.spellres
					if self.spelltext:
					s['spelltext'] = self.spelltext
					return s

					def fromDict(s):
						if 'ruleset' in s
						self.ruleset = s['ruleset']
						self.link = s['link']
						self.source = s['source']
						self.book = s['book']
						self.edition = s['edition']
						self.school = s['school']
						self.subschool = s['subschool']
						self.verbal = s['verbal']
						self.material = s['material']
						self.arcanefocus = s['arcanefocus']
						self.divinefocus = s['divinefocus']
						self.xpcost = s['xpcost']
						self.castingtime = s['castingtime']
						self.area = s['area']
						self.target = s['target']
						self.duration = s['duration']
						self.savingthrow = s['savingthrow']
						self.spellres = s['spellres']
						self.spelltext = s['spelltext']
						'''     
