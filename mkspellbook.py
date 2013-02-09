#!/usr/bin/env python3
#templatetest

import sqlite3
import re
import argparse

global conditionregexp 
conditionregexp = re.compile('\[\[\?(?P<condition>[^\|]*)\|(?P<string>[^\?]*)\?\]\]')
global replacevarregexp 
replacevarregexp = re.compile('\[\[(?P<var>[^\]]*)\]\]')


def replace(dictionary, string):
    return replacevarregexp.sub(lambda p : texify(str(dictionary[p.group("var")])), string)

def condition(dictionary, string):
    return conditionregexp.sub(lambda m : replace(dictionary, m.group("string")) if m.group("condition") in dictionary and dictionary[m.group("condition")] else "", string)

def write(output, string):
    if output:
        output.write(string)
    else:
        print(string)

def texify(string):
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
    
parser = argparse.ArgumentParser(description="Creates a Spellbook")
parser.add_argument("--template", "-t", default="plain")
parser.add_argument("--output", "-o", type=argparse.FileType('w'), metavar="FILE")
parser.add_argument("--input", "-i", type=argparse.FileType('r'), default="selection", metavar="FILE")
args = parser.parse_args()
templatepath = "templates/" + args.template + "/"

template = open(templatepath + 'spell.tex', 'r')
templatestring = template.read()

con = sqlite3.connect("spells.db")
con.row_factory = sqlite3.Row
spellcur = con.cursor()
descriptorcur = con.cursor()

spellsfile = args.input.read().split()
spells="id = \"None\""
for i in range(int(len(spellsfile)/2)):
	spells += " or (id = "+spellsfile[2*i] + " and class = '" + spellsfile[2*i+1] + "')"

spellcur.execute("select * from spells join levels on spells.id = levels.spell where " + spells + " order by level,name;")

head = open(templatepath + 'head.tex', 'r')
write(args.output, head.read())
row = spellcur.fetchone()
currlevel = row['level']
write(args.output, "\\chapter{Level " + str(currlevel) + "}")
while row is not None:
    if currlevel != row['level']:
        currlevel = row['level']
        write(args.output, "\\chapter{Level " + str(currlevel) + "}")
    dictrow = dict(row)
    descriptorcur.execute("select descriptor from descriptors where spell = " + str(row['id']))
    drow = descriptorcur.fetchone()
    dictrow['descriptor'] = ""
    while drow is not None:
        dictrow['descriptor'] += "[" + drow['descriptor'] + "] "
        drow = descriptorcur.fetchone()
    cond = condition(dictrow, templatestring)
    replaced = replace(dictrow, cond)
    write(args.output, replaced)
    row = spellcur.fetchone()
tail = open(templatepath + 'tail.tex', 'r')
write(args.output, tail.read())

if args.output:
    args.output.close()

