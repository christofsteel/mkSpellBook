from sqlalchemy.orm import sessionmaker
from mkSpellbook.models import *


class Spells:
	def __init__(self, database):
		engine = create_engine("sqlite:///" + database)
		Session = sessionmaker(bind=engine)
		self.session = Session()		
		Base.metadata.create_all(engine)

	def listRulesets(self):
		return [spell.ruleset for spell in self.session.query(Spell.ruleset).distinct()]

	def listClasses(self, ruleset):
		query = self.session.query(ClassLevel.d20class).filter(ClassLevel.spells.any(Spell.ruleset == ruleset)).distinct().all()
		return [cl.d20class for cl in query]

	def listBooks(self, ruleset, d20class):
		query = self.session.query(Spell.book, Spell.edition)
		query = query.filter(Spell.ruleset == ruleset)
		query = query.filter(Spell.classlevels.any(ClassLevel.d20class == d20class))
		return query.distinct().order_by(Spell.edition, Spell.book).all()

	def listLevels(self, ruleset, d20class, book):
		query = self.session.query(ClassLevel.level)
		query = query.filter(ClassLevel.spells.any(Spell.ruleset == ruleset)).filter(ClassLevel.spells.any(Spell.book ==  book))
		query = query.filter(ClassLevel.d20class == d20class)
		return [cl.level for cl in query.distinct()]

	def listSpells(self, ruleset, d20class, book, level):
		query = self.session.query(Spell)
		query = query.filter(Spell.ruleset == ruleset, Spell.book == book)
		query = query.filter(Spell.s2cl.classlevels.any(d20class = d20class, level = level))
		return query.all()
	
	def listSpellsWithClasslevels(self, ruleset, d20class, book, level):
		query = self.session.query(SpellWithClasslevel)
		query = query.filter(SpellWithClasslevel.spell.has(Spell.ruleset==ruleset), SpellWithClasslevel.spell.has(Spell.book == book))
		query = query.filter(SpellWithClasslevel.classlevel.has(ClassLevel.d20class == d20class), SpellWithClasslevel.classlevel.has(ClassLevel.level == level))
		return query.all()

	def listSpellbooks(self):
		return self.session.query(Spellbook).all()

	def getSpellbook(self, spellbook):
		return self.session.query(Spellbook).filter(Spellbook.name == spellbook).first() or Spellbook(name = spellbook)
	
	def getDescriptor(self, descriptor):
		return self.session.query(Descriptor).filter(Descriptor.descriptor == descriptor).first() or Descriptor(descriptor)

	def getClassLevel(self, d20class, level):
		return self.session.query(ClassLevel).filter(ClassLevel.d20class == d20class, ClassLevel.level == level).first() or ClassLevel(d20class, level)

	def addSpell(self, spell):
		self.session.add(spell)
		self.session.commit()
