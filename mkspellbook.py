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
    return conditionregexp.sub(lambda m : replace(dictionary, m.group("string")) if m.group("condition") in dictionary else "", string)


template = open('spell.tex', 'r')
templatestring = template.read()


con = sqlite3.connect("spells.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
cur.execute("select * from spells WHERE id = 2 OR id = 5 OR id = 1634 OR id = 744 OR id = 9;")


head = open('head.tex', 'r')
print(head.read())
row = cur.fetchone()
while row is not None:
    cond = condition(row, templatestring)
    replaced = replace(row, cond)
    print(replaced)
    row = cur.fetchone()

tail = open('tail.tex', 'r')
print(tail.read())
