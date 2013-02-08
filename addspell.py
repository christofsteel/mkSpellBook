#!/usr/bin/env python3

import sqlite3

def askString(prompt, required = False, default="", multiline = False):
	if default:
		defaultstring = " (Default: " + default + ")"
	else:
		defaultstring = ""
	if multiline:
		multilinestring = "[Insert an empty line to finish, expected HTML Syntax]"
	else:
		multilinestring = ""

	value = input(prompt + defaultstring + multilinestring + ": ")
	if required and not value:
		print("Field is required, cannot be empty!")
		return askString(prompt, required, default, multiline)
	else:
		if value:
			if multiline:
				line = value
				while line:
					line = input("> ")
					value += "\n" + line
				print(value)
			return value

		else:
			return default or None

def askDescriptor():
	descriptors = input("Descriptors (Syntax: Descriptor Descriptor ...): ")
	return descriptors.split()

def askClasses(functions=[str, int]):
	levels = input("Class/Level (Syntax: Class Level Class Level Class Level ...): ")
	if not levels:
		print("Field is required, cannot be empty!")
		return askClasses(functions)
	else:
		levelssplit = levels.split()
		d = {}
		for i in range(0, len(levelssplit), 2):
			d[functions[0](levelssplit[i])] = functions[1](levelssplit[i+1])
		return d
	

def askBool(prompt):
	value = input(prompt + "? ")
	if value:
		return 1
	else:
		return 0

spell = {}
spell['name'] = askString("Spell Name", True)
spell['ruleset'] = askString("Ruleset", False, "D&D 3.5")
spell['edition'] = askString("Edition", False, "Supplementals (3.5)")
spell['book'] = askString("Book", False, "Homebrew") 
spell['levels'] = askClasses()
spell['school'] = askString("School", True)
spell['subschool'] = askString("Subschool")
spell['descriptors'] = askDescriptor()
spell['verbal'] = askBool("Verbal")
spell['somatic'] = askBool("Somatic")
spell['material'] = askBool("Material")
spell['arcanefocus'] = askBool("Arcane Focus")
spell['divinefocus'] = askBool("Divine Focus")
spell['xpcost'] = askBool("XP Cost")
spell['castingtime'] = askString("Casting Time")
spell['spellrange'] = askString("Spell Range")
spell['area'] = askString("Area")
spell['target'] = askString("Target")
spell['duration'] = askString("Duration")
spell['savingthrow'] = askString("Saving Throw")
spell['spellres'] = askString("Spell Resistance")
spell['spelltext'] = askString("Spell Text", True, multiline=True)

keys = "name"
values = "\""+spell['name']+"\""
con = sqlite3.connect("spells.db")
cur = con.cursor()
cur.execute("select count(id) from spells")
spell['id'] = int(cur.fetchall()[0][0])+1
for k in ["id", "ruleset",  "book", "edition","school", "subschool", "verbal", "somatic", "material", "arcanefocus", "divinefocus", "xpcost"    , "castingtime", "target", "duration", "savingthrow", "spellres", "spelltext"]:
	if spell[k]:
		keys = keys + "," + k
		values = values + "," + "\""+ str(spell[k]) + "\""		
query = "INSERT INTO spells (" + keys + ") VALUES ("+values+");"
cur.execute(query)
for k, v in spell['levels'].items():
	levelquery = "INSERT INTO levels (spell, class, level) VALUES (\"" + str(spell['id']) + "\", \"" + k + "\", \"" + str(v) +"\");"
	cur.execute(levelquery)

if 'descriptors' in spell:
	for descriptor in spell['descriptors']:
		descquery = "INSERT INTO descriptors (spell, descriptor) VALUES (\"" + str(spell['id']) + "\", \"" + descriptor + "\");"
		cur.execute(descquery)

con.commit()
