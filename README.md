# mkSpellBook #

Generates a D&amp;D 3rd Edition (3.0 and 3.5) spellbook based on the spells available on dndtools.eu

## Prerequirements ##

You need python3, pyquery, sqlite3

## Usage ##
To build your spell data base, run

    python update.py
  
This generates you a `spells.db` with all the spells available on dndtools.eu.

## Schema ##

The Database contains 3 tables:

spells:
    CREATE TABLE spells (id integer primary key, link text, name text, book text, edition text, school, subschool, verbal integer, somatic integer, material integer, arcanefocus integer, divinefocus integer, xpcost integer, castingtime text, spellrange text, area text, target text, duration text, savingthrow text, spellres text, spelltext text);

levels:
    CREATE TABLE levels (spell integer, class text, level integer, FOREIGN KEY(spell) REFERENCES spells(id));

descriptors:
    CREATE TABLE descriptors (spell integer, descriptor text,FOREIGN KEY(spell) REFERENCES spells(id));

enjoy.
