#!/usr/bin/env python
from pyquery import PyQuery as pq
from mkSpellbook.models import *
from mkSpellbook.spells import *
from mkSpellbook.dialog import Gauge
import re
import sqlite3
import urllib

def runimport(database):
	spells = Spells(database)
	pages = []
	gauge = Gauge("Downloading spell lists")
	gauge.show()
	pages.append(pq(url='http://dndtools.eu/spells/?page_size=1000'))
	perc = 25
	gauge.update(perc)
	pages[0].make_links_absolute()
	while pages[-1]('.pagination .next').eq(0).attr('href'):
		pages.append(pq(url=pages[-1]('.pagination .next').eq(0).attr('href')))
		pages[-1].make_links_absolute()
		perc += 25
		gauge.update(perc)

	spellid = 1
	htmlspells = []
	for page in pages:
		htmlspells.extend(list(page('.common').children().items())[1:])
	index = 1
	for spell in htmlspells[1:]:
		s = Spell()
		s.link = spell.children().eq(0).children().attr('href')
		s.name = spell.children().eq(0).children().text()
		gauge.update(int(index/len(htmlspells)*100),"Downloading Spell: " + s.name + " ("+str(index)+"/"+str(len(htmlspells))+")")
		s.book = spell.children().eq(3).children().text()
		s.edition = spell.children().eq(4).children().text()
		dnd30 = ['Oriental Adventures', 'Supplementals (3.0)' , 'Forgotten Realms (3.0)']
		dnd35 = ['Forgotten Realms (3.5)' , 'Supplementals (3.5)' , 'Core (3.5)' , 'Eberron (3.5)']
		s.ruleset = "D&D 3.5" if s.edition in dnd35 else ("D&D 3.0" if s.edition in dnd30 else "Other")
		s.school = spell.children().eq(1).children().text()
		s.verbal = int(spell.children().eq(2).children().eq(0).attr('alt') == 'yes')
		s.somatic = int(spell.children().eq(2).children().eq(1).attr('alt') == 'yes')
		s.material = int(spell.children().eq(2).children().eq(2).attr('alt') == 'yes')
		s.arcanefocus = int(spell.children().eq(2).children().eq(3).attr('alt') == 'yes')
		s.divinefocus = int(spell.children().eq(2).children().eq(4).attr('alt') == 'yes')
		s.xpcost = int(spell.children().eq(2).children().eq(5).attr('alt') == 'yes')
		spelldetail = pq(url=s.link)

		mSubschool = re.search("<a href=\"/spells/sub-schools/.*\">(?P<subschool>.*)</a>", spelldetail('#content').html())
		if mSubschool:
			s.subschool = mSubschool.group("subschool")

		
		for mDescriptor in re.finditer("<a href=\"/spells/descriptors/[^\"]*\">(?P<descriptor>[^<]*)</a>", spelldetail('#content').html()):
			s.descriptors.append(spells.getDescriptor(mDescriptor.group("descriptor")))
		keywords = list(spelldetail('#content strong').items())
		for i, keyword in enumerate(keywords):
			ktext = keyword.text()
			if ktext == "Level:": # ugly fuck
				for m in  re.finditer("<a href=\"/classes/.*\">(?P<class>[A-Za-z]*) (?P<level>[0-9]*)</a>", spelldetail('#content').html()):
					s.s2cl.append(SpellWithClasslevel(spell=s, classlevel=spells.getClassLevel(m.group("class"), int(m.group("level")))))
			elif ktext != "Components:":
				mKeyword = re.search("<strong>"+ktext+"</strong> (?P<text>[^<]*)", spelldetail('#content').html())
				if ktext == "Casting Time:":
					s.castingtime = mKeyword.group("text")
				elif ktext == "Range:":
					s.spellrange = mKeyword.group("text")
				elif ktext == "Area:":
					s.area = mKeyword.group("text")
				elif ktext == "Target:":
					s.target = mKeyword.group("text")
				elif ktext == "Duration:":
					s.duration = mKeyword.group("text")
				elif ktext == "Saving Throw:":
					s.savingthrow = mKeyword.group("text")
				elif ktext == "Spell Resistance:":
					s.spellres = mKeyword.group("text")
		s.spelltext =re.sub("\"", "''",  spelldetail('#content .nice-textile').html())
		spells.addSpell(s)
		index += 1
	gauge.close()
