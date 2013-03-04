# mkSpellBook #

Generate and organize Spellbooks for d20 based role playing games.

## Prerequirements ##

You need python3, pyquery, sqlite3 and sqlalchemy. 
If you want to use the fancy or fancybw template, you need [pfgornaments](http://altermundus.com/pages/tkz/ornament/index.html).

## Install ##

Install using easy_install, pip or simply run `python setup.py install` 
If you are using Arch Linux, you can use the PKGBUILD

## Usage ##

To start the program start

    mkspellbook

and add spells via the import scripts.

## Advanced ##

### Templates ###

mkSpellbook is shipped with 3 templates: plain, fancy, fancybw 
To create a template add a folder in `~/.mkspellbook/templates` with at least 3 files:

  * head.tex
  * spell.tex
  * tail.tex

#### Variables ####

You can use a variable with `[[var]]`. If you want to check, if a variable exists and is not empty, use `[[?var|CODE?]]` `CODE` is inserted only, of `var` exists and is not empty.

##### head.tex #####
head.tex is inserted at the start of your spellbook
Variables:

  * title 
  * author
  * logo

##### spell.tex #####
spell.tex is repeated for every selected spells.
Variables:

  * name
  * link
  * ruleset
  * edition
  * book
  * d20class
  * level
  * school
  * subschool
  * descriptors
  * verbal
  * somatic
  * material
  * arcanefocus
  * divinefocus
  * xpcost
  * castingtime
  * spellrange
  * area
  * target
  * duration
  * savingthrow
  * spellres
  * spelltext

###### tail.tex ######
tail.tex is inserted at the end of your spellbook.

### Import Scripts ###

To create your own importscripts, add a pythonfile `script_YOURSCRIPT.py` to `~/.mkspellbook/importscripts`. 
It should have a function called `runimport(database)`.

### Print as booklet ###
If you want to generate a booklet, this might help:

    pdf2ps yourspellbook.pdf 
    psbook yourspellbook.ps yourspellbook_book.ps
    psnup -s1 -2 yourspellbook_book.ps yourspellbook_booklet.ps
    ps2pdf yourspellbook_booklet.ps yourspellbook_booklet.pdf
    rm yourspellbook.ps yourspellbook_book.ps yourspellbook_booklet.ps
