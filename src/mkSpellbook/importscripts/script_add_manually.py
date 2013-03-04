from mkSpellbook.spells import *
from mkSpellbook.dialog import *
from mkSpellbook.models import *

def runimport(database):
	spells = Spells(database)
	d = Dialog()
	fields = [	("Name", "Spell Name", 50),
			("Ruleset", "D&D 3.5", 50),
			("Edition","Homebrew",50),
			("Book","Homebrew Book I",50),
			("Class/Level", "Cleric 1, Sorcerer 1", 50),
			("School","",50),
			("Subschool","",50),
			("Descriptors","Evil, Good",50),
			("Verbal","1",50),
			("Somatic","0",50),
			("Material","1",50),
			("Arcane Focus","0",50),
			("Divine Focus","1",50),
			("XP Cost","0",50),
			("Casting Time","",50),
			("Range","",50),
			("Area","",50),
			("Target","",50),
			("Duration","",50),
			("Saving Throw","",50),
			("Spell Resistance","",50),
			("Link","",50)]
	frc, fch = d.form("Add Spells", fields=fields)
	if fch and not frc:
		choices = fch.split("\n")
		s = Spell()
		s.name = choices[0]
		s.ruleset = choices[1]
		s.edition = choices[2]
		s.book = choices[3]
		s.s2cl = [SpellWithClasslevel(spell=s, classlevel=spells.getClassLevel(cl[0], int(cl[1]))) for cl in [classlevel.split() for classlevel in choices[4].split(",")]]
		s.school = choices[5]
		s.subschool = choices[6]
		s.descriptors = [spells.getDescriptor(desc.strip()) for desc in choices[7].split(",")]
		s.verbal = choices[8] and choices[7] != "0"
		s.somatic = choices[9] and choices[8] != "0"
		s.material = choices[10] and choices[9] != "0"
		s.arcanefocus = choices[11] and choices[10] != "0"
		s.divinefocus = choices[12] and choices[11] != "0"
		s.xpcost = choices[13] and choices[12] != "0"
		s.castingtime = choices[14]
		s.spellrange = choices[15]
		s.area = choices[16]
		s.target = choices[17]
		s.duration = choices[18]
		s.savingthrow = choices[19]
		s.spellres = choices[20]
		s.link = choices[21]
		s.spelltext = "Foobar"
		spells.session.add(s)
		spells.session.commit()
