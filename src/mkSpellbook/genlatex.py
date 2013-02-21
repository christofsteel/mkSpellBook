#!/usr/bin/env python3
#templatetest

import sqlite3
import re
import argparse
import subprocess
import hashlib
import os
from mkSpellbook.spells import Spells

class Genlatex:
	def __init__(self):
		self.conditionregexp = re.compile('\[\[\?(?P<condition>[^\|]*)\|(?P<string>[^\?]*)\?\]\]')
		self.replacevarregexp = re.compile('\[\[(?P<var>[^\]]*)\]\]')


	def replace(self, dictionary, string):
		return self.replacevarregexp.sub(lambda p : self.texify(str(dictionary[p.group("var")])), string)

	def insertTemplate(self, dictionary, string):
		decondition =  self.conditionregexp.sub(lambda m : self.replace(dictionary, m.group("string")) if m.group("condition") in dictionary and dictionary[m.group("condition")] else "", string)
		replaced = self.replace(dictionary, decondition)
		return replaced

	def texify(self, string):
		replacements = {
			"<li>": r"\\item ",
			"</li>": r"\n",
			"<ul>": r"\\begin{itemize}\n",
			"<br/>|<p>": r"\\\\ \n",
			"</ul>(\s|<br/>|<p>)*": r"\\end{itemize}\n",
			"<em>": r"\\textit{",
			"<a[^>]*>|</a>": r"",
			"<sup>": r"\\textsuperscript{",
			"\"": r"''",
			"</em>|</sup>": r"}",
			"%":r"\\%",
			"&": r" \\& ",
			u'\uFB02': r"fl", 
			"_": r"\\_",
			"×": r"x",
			"<span[^>]*>|</span>":r"",
			"<table>.*</table>": r"TODO Tabelle parsen"
			}
		string = re.sub("^\s*<p>|&#13;|</p>|\r|\n|\t", "", string)
		string = re.sub("&amp;", "&", string)
		for k, v in replacements.items():
			string = re.sub(k, v, string, flags=re.UNICODE)
		return string
	
	def genlatex(self, spellbookpath, spellbookname, spells, selectedspells, templatepath, author, logo):
		spellbookbasename = spellbookpath + "/" + spellbookname + "/" + spellbookname
		spellbookfilename = spellbookpath + "/" + spellbookname + "/" + spellbookname + ".tex"
		spellbookpdfname = spellbookpath + "/" + spellbookname + "/" + spellbookname + ".pdf"
		spellbookfile = open(spellbookfilename, 'w')
		template = open(templatepath + 'spell.tex', 'r')
		templatestring = template.read()
		template.close()
		head = open(templatepath + 'head.tex', 'r')
		spellbookfile.write(self.insertTemplate({'author': author, 'logo': logo, 'title': spellbookname}, head.read()))
		head.close()
		currlevel = -1
		for spell in spells.getSpellsByTuple(selectedspells):
			if currlevel != spell['level']:
				currlevel = spell['level']
				spellbookfile.write("\\chapter{Level " + str(currlevel) + "}")
			spellbookfile.write(self.insertTemplate(spell, templatestring))
		tail = open(templatepath + 'tail.tex', 'r')
		spellbookfile.write(tail.read())
		tail.close()
		spellbookfile.close()

		subprocess.call(["pdflatex", "-output-directory", spellbookpath + "/" + spellbookname, spellbookfilename])
		subprocess.call(["pdflatex", "-output-directory", spellbookpath + "/" + spellbookname, spellbookfilename])
		subprocess.call(["pdflatex", "-output-directory", spellbookpath + "/" + spellbookname, spellbookfilename])

		os.remove(spellbookbasename + ".aux")
		os.remove(spellbookbasename + ".toc")
		os.remove(spellbookbasename + ".log")

