from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import or_
from mkSpellbook.models import *


class Spells:
	def __init__(self, database):
		engine = create_engine("sqlite:///" + database)
		Session = sessionmaker(bind=engine)
		self.session = Session()		
		Base.metadata.create_all(engine)

	def listRulesets(self):
		return [spell.ruleset for spell in self.session.query(Spell.ruleset).distinct()]

	def listClasses(self, rulesets):
		clause = [Spell.ruleset == ruleset for ruleset in rulesets]
		query = self.session.query(ClassLevel.d20class).filter(ClassLevel.spells.any(or_(*clause))).distinct().all()
		return [cl.d20class for cl in query]

	def listBooks(self, rulesets, d20classes):
		query = self.session.query(Spell.book, Spell.edition)
		query = query.filter(or_(*[Spell.ruleset == ruleset for ruleset in rulesets]))
		query = query.filter(Spell.classlevels.any(or_(*[ClassLevel.d20class == d20class for d20class in d20classes])))
		result = query.distinct().order_by(Spell.edition, Spell.book).all()
		return [[book.book, book.edition] for book in result]

	def listLevels(self, rulesets, d20classes, books):
		query = self.session.query(ClassLevel.level)
		query = query.filter(ClassLevel.spells.any(or_(*[Spell.ruleset == ruleset for ruleset in rulesets])))
		query = query.filter(ClassLevel.spells.any(or_(*[Spell.book ==  book[0] for book in books])))
		query = query.filter(or_(*[ClassLevel.d20class == d20class for d20class in d20classes]))
		return [cl.level for cl in query.distinct()]

	def listSpells(self, ruleset, d20class, book, level):
		query = self.session.query(Spell)
		query = query.filter(Spell.ruleset == ruleset, Spell.book == book)
		query = query.filter(Spell.s2cl.classlevels.any(d20class = d20class, level = level))
		return query.all()
	
	def listSpellsWithClasslevels(self, rulesets = [], d20classes = [], books = [], levels = [], filterstring = ""):
		query = self.session.query(SpellWithClasslevel)
		query = query.filter(SpellWithClasslevel.spell.has(or_(*[Spell.ruleset==ruleset for ruleset in rulesets])), SpellWithClasslevel.spell.has(or_(*[Spell.book == book for book in books])))
		query = query.filter(SpellWithClasslevel.classlevel.has(or_(*[ClassLevel.d20class == d20class for d20class in d20classes])), SpellWithClasslevel.classlevel.has(or_(*[ClassLevel.level == level for level in levels])))
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
