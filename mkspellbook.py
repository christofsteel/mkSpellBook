#!/usr/bin/env python3
#templatetest

import sqlite3
import re

global conditionregexp 
conditionregexp = re.compile('\[\[\?(?P<condition>[^\|]*)\|(?P<string>[^\?]*)\?\]\]')
global replacevarregexp 
replacevarregexp = re.compile('\[\[(?P<var>[^\]]*)\]\]')


def replace(dictionary, string):
    return replacevarregexp.sub(lambda p : dictionary[p.group("var")], string)

def condition(dictionary, string):
    return conditionregexp.sub(lambda m : replace(dictionary, m.group("string")) if m.group("condition") in dictionary and dictionary[m.group("condition")] else "", string)


template = open('spell.tex', 'r')
templatestring = template.read()


con = sqlite3.connect("spells.db")
con.row_factory = sqlite3.Row
spellcur = con.cursor()
descriptorcur = con.cursor()

spellcur.execute("select * from spells join levels on spells.id = levels.spell where (edition = 'Core (3.5)' or edition = 'Forgotten Realms (3.5)' or edition = 'Supplementals (3.5)') order by level,name;")

head = open('head.tex', 'r')
print(head.read())
row = spellcur.fetchone()
while row is not None:
    dictrow = dict(row)
    descriptorcur.execute("select descriptor from descriptors where spell = " + str(row['id']))
    drow = descriptorcur.fetchone()
    dictrow['descriptor'] = ""
    while drow is not None:
        dictrow['descriptor'] += drow['descriptor']
        drow = descriptorcur.fetchone()
    cond = condition(dictrow, templatestring)
    replaced = replace(dictrow, cond)
    print(replaced)
    row = spellcur.fetchone()
tail = open('tail.tex', 'r')
print(tail.read())
