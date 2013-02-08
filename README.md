# mkSpellBook #

Generates a D&amp;D 3rd Edition (3.0 and 3.5) spellbook based on the spells available on dndtools.eu

## Prerequirements ##

You need python3, pyquery, sqlite3.  
If you want to use the fancy template, you need [pfgornaments](http://altermundus.com/pages/tkz/ornament/index.html).

## Usage ##
To build your spell database, run

    ./update.py
  
This generates you a `spells.db` with all the spells available on dndtools.eu.

To add a spell manually, run
   
    ./addspell.py

To select your spells, run

    ./selector.py

To generate your Spellbook, run

    python mkspellbook.py -o yourspellbook.py
    
### Print as booklet ###
If you want to generate a booklet, this might help:

    pdflatex yourspellbook.tex
    pdflatex yourspellbook.tex
    pdflatex yourspellbook.tex # 3 times for the correct table of contents
    pdf2ps yourspellbook.pdf 
    psbook yourspellbook.ps yourspellbook_book.ps
    psnup -s1 -2 yourspellbook_book.ps yourspellbook_booklet.ps
    ps2pdf yourspellbook_booklet.ps yourspellbook_booklet.pdf
    rm yourspellbook.ps yourspellbook_book.ps yourspellbook_booklet.ps
    

## Template ##
mkSpellBook supports templates. Just create a new folder in `templates/`. See `templates/plain/' for an example.  
Run `./mkspellbook.py -t [template]` to use a template.

## Schema ##

The Database contains 3 tables:

spells:

    CREATE TABLE spells (id integer primary key, ruleset text, link text, name text, book text, edition text, school, subschool, verbal integer, somatic integer, material integer, arcanefocus integer, divinefocus integer, xpcost integer, castingtime text, spellrange text, area text, target text, duration text, savingthrow text, spellres text, spelltext text);

levels:

    CREATE TABLE levels (spell integer, class text, level integer, FOREIGN KEY(spell) REFERENCES spells(id));

descriptors:

    CREATE TABLE descriptors (spell integer, descriptor text,FOREIGN KEY(spell) REFERENCES spells(id));

enjoy.
