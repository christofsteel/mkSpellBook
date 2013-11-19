#!/usr/bin/env python3
#templatetest

import re
import subprocess
import os
import os.path
import shutil
import tempfile
import traceback
from mkSpellbook.spells import Spells
from mkSpellbook.models import *

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
			"<br/>": r"\\\\ \n",
			"</p>": r"\\\\ \n",
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
		string = re.sub("^\s*<p>|&#13;|<p>|\r|\n|\t", "", string)
		string = re.sub("&amp;", "&", string)
		for k, v in replacements.items():
			string = re.sub(k, v, string, flags=re.M)
		return string
	
	def genlatex(self, spellbook, templatepath, output):
		temppath = tempfile.TemporaryDirectory(prefix="mkSpellbook-")
		temptex = tempfile.NamedTemporaryFile(dir=temppath.name, delete=False, suffix=".tex", mode="w")
		templogo = None
		if spellbook.logo:
			templogo = tempfile.NamedTemporaryFile(dir=temppath.name, delete=False, suffix=spellbook.logoext)
			templogo.write(spellbook.logo)
			templogo.close()


		try:
			with open(templatepath + 'resources', 'r') as resourcesfile:
				resources = [r.strip() for r in resourcesfile.readlines()]
				for resource in resources:
					try:
						print(os.path.join(temppath.name,resource))
						print(os.path.join(templatepath,resource))
						shutil.copy(os.path.join(templatepath,resource),os.path.join(temppath.name,
							resource))
					except Exception:
						print("Something went wrong copying %s" % resource)
						traceback.print_exc()
		except Exception:
			print("Could not read resources")
		template = open(templatepath + 'spell.tex', 'r')
		templatestring = template.read()
		template.close()
		head = open(templatepath + 'head.tex', 'r')
		temptex.write(self.insertTemplate({'author': spellbook.author, 'logo': templogo.name if spellbook.logo else None, 'title': spellbook.name}, head.read()))
#		temptex.write(self.insertTemplate({'author': spellbook.author, 'title': spellbook.name}, head.read()))
		head.close()
		currlevel = -1
		for spell in spellbook.spells:
			spelldict = spell.classlevel.__dict__
			spelldict.update(spell.spell.__dict__)
			if currlevel != spelldict['level']:
				currlevel = spelldict['level']
				temptex.write("\\chapter{Level " + str(currlevel) + "}")
			temptex.write(self.insertTemplate(spelldict, templatestring))
		tail = open(templatepath + 'tail.tex', 'r')
		temptex.write(tail.read())
		tail.close()
		temptex.close()
		cwd = os.getcwd()
		os.chdir(temppath.name)
		subprocess.call(["pdflatex", "-output-directory", temppath.name, temptex.name])
		subprocess.call(["pdflatex", "-output-directory", temppath.name, temptex.name])
		subprocess.call(["pdflatex", "-output-directory", temppath.name, temptex.name])
		os.chdir(cwd)
		
		pdfname = os.path.splitext(temptex.name)[0] + ".pdf"
		shutil.copy(pdfname, output)

