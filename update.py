#!/usr/bin/env python3

from pyquery import PyQuery as pq
from collections import namedtuple
import re
import sqlite3
import urllib

conn = sqlite3.connect('spells.db')
c = conn.cursor()
c.execute("CREATE TABLE spells (id integer primary key, ruleset text, link text, name text, book text, edition text, school, subschool, verbal integer, somatic integer, material integer, arcanefocus integer, divinefocus integer, xpcost integer, castingtime text, spellrange text, area text, target text, duration text, savingthrow text, spellres text, spelltext text);")
c.execute("CREATE TABLE levels (spell integer, class text, level integer, FOREIGN KEY(spell) REFERENCES spells(id));")
c.execute("CREATE TABLE descriptors (spell integer, descriptor text,FOREIGN KEY(spell) REFERENCES spells(id));")

pages = []
pages.append(pq(url='http://dndtools.eu/spells/?page_size=1000'))
print("Loaded first page")
pages[0].make_links_absolute()
while pages[-1]('.pagination .next').eq(0).attr('href'):
    print(pages[-1]('.pagination .next').eq(0).attr('href'))
    pages.append(pq(url=pages[-1]('.pagination .next').eq(0).attr('href')))
    pages[-1].make_links_absolute()

spellid = 1
for page in pages:
    spells = list(page('.common').children().items())
    for spell in spells[1:]:
        s = dict()
        s['id'] = spellid
        s['link'] = spell.children().eq(0).children().attr('href')
        s['name'] = spell.children().eq(0).children().text()
        s['book'] = spell.children().eq(3).children().text()
        s['edition'] = spell.children().eq(4).children().text()
        dnd30 = ['Oriental Adventures', 'Supplementals (3.0)' , 'Forgotten Realms (3.0)']
        dnd35 = ['Forgotten Realms (3.5)' , 'Supplementals (3.5)' , 'Core (3.5)' , 'Eberron (3.5)']
        s['ruleset'] = "D&D 3.5" if s['edition'] in dnd35 else ("D&D 3.0" if s['edition'] in dnd30 else "Other")
        s['school'] = spell.children().eq(1).children().text()
        s['verbal'] = int(spell.children().eq(2).children().eq(0).attr('alt') == 'yes')
        s['somatic'] = int(spell.children().eq(2).children().eq(1).attr('alt') == 'yes')
        s['material'] = int(spell.children().eq(2).children().eq(2).attr('alt') == 'yes')
        s['arcanefocus'] = int(spell.children().eq(2).children().eq(3).attr('alt') == 'yes')
        s['divinefocus'] = int(spell.children().eq(2).children().eq(4).attr('alt') == 'yes')
        s['xpcost'] = int(spell.children().eq(2).children().eq(5).attr('alt') == 'yes')
        spelldetail = pq(url=s['link'])

        mSubschool = re.search("<a href=\"/spells/sub-schools/.*\">(?P<subschool>.*)</a>", spelldetail('#content').html())
        if mSubschool:
            s['subschool'] = mSubschool.group("subschool")

        s['descriptor'] = []
        for mDescriptor in re.finditer("<a href=\"/spells/descriptors/[^\"]*\">(?P<descriptor>[^<]*)</a>", spelldetail('#content').html()):
            s['descriptor'].append(mDescriptor.group("descriptor"))

        s['levels'] = dict()                

        keywords = list(spelldetail('#content strong').items())
        for i, keyword in enumerate(keywords):
            ktext = keyword.text()
            if ktext == "Level:": # ugly fuck
                for m in  re.finditer("<a href=\"/classes/.*\">(?P<class>[A-Za-z]*) (?P<level>[0-9]*)</a>", spelldetail('#content').html()):
                     s['levels'][m.group("class")] = m.group("level")
            elif ktext != "Components:":
                mKeyword = re.search("<strong>"+ktext+"</strong> (?P<text>[^<]*)", spelldetail('#content').html())
                if ktext == "Casting Time:":
                    s['castingtime'] = mKeyword.group("text")
                elif ktext == "Spell Range:":
                    s['spellrange'] = mKeyword.group("text")
                elif ktext == "Area:":
                    s['area'] = mKeyword.group("text")
                elif ktext == "Target:":
                    s['target'] = mKeyword.group("text")
                elif ktext == "Duration:":
                    s['duration'] = mKeyword.group("text")
                elif ktext == "Saving Throw:":
                    s['savingthrow'] = mKeyword.group("text")
                elif ktext == "Spell Resistance:":
                    s['spellres'] = mKeyword.group("text")
        s['spelltext'] =re.sub("\"", "''",  spelldetail('#content .nice-textile').html())
        print(s['name']);
        keys = "name"
        values = "\""+s['name']+"\""
        for k in ["id", "ruleset", "link", "book", "edition","school", "subschool", "verbal", "somatic", "material", "arcanefocus", "divinefocus", "xpcost", "castingtime", "target", "duration", "savingthrow", "spellres", "spelltext"]:
            if k in s:
                keys = keys + "," + k 
                values = values + "," + "\""+ str(s[k]) + "\""
        query = "INSERT INTO spells (" + keys + ") VALUES ("+values+");"
#        print(query)
        c.execute(query)

        #levels
        for k, v in s['levels'].items():
            levelquery = "INSERT INTO levels (spell, class, level) VALUES (\"" + str(s['id']) + "\", \"" + k + "\", \"" + str(v) +"\");"
            c.execute(levelquery)

        #Descriptors
        if 'descriptor' in s:
            for descriptor in s['descriptor']:
                descquery = "INSERT INTO descriptors (spell, descriptor) VALUES (\"" + str(s['id']) + "\", \"" + descriptor + "\");"
                c.execute(descquery)

        spellid = spellid + 1
    conn.commit()
