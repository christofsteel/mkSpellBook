from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from mkSpellbook.models import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound


class Spells:
	def __init__(self, database):
		engine = create_engine(database)
		Session = sessionmaker(bind=engine)
		self.session = Session()		
		Base.metadata.create_all(engine)

	def listRulesets(self):
		return [spell.ruleset for spell in self.session.query(Spell.ruleset).distinct()]

	def listClasses(self, ruleset):
		query = self.session.query(ClassLevel.d20class)
		query = query.filter(ClassLevel.spells.any(Spell.ruleset == ruleset))
		return [cl.d20class for cl in query.distinct()]

	def listBooks(self, ruleset, d20class):
		query = self.ession.query(Spell.book, Spell.edition)
		query = query.filter(Spell.ruleset == ruleset)
		query = query.filter(Spell.classlevels.any(ClassLevel.d20class == d20class))
		return query.distinct().all()

	def listLevels(self, ruleset, d20class, book):
		query = self.session.query(ClassLevel.level)
		query = query.filter(ClassLevel.spells.any(Spell.ruleset == ruleset, Spell.book == book))
		query = query.filter(ClassLevel.d20class == d20class)
		return [cl.level for cl in query.distinct()]

	def listSpells(self, ruleset, d20class, book, level):
		query = self.session.query(Spells)
		query = query.filter(Spell.ruleset == ruleset, Spell.book == book)
		query = query.filter(Spell.classlevels.any(ClassLevel.d20class == d20class, ClassLevel.level == level))
		return query.all()
	
	def mkDescriptors(self, descriptors):
		return [self.session.query(Descriptor).filter(Descriptor.descriptor == descriptor).first() or Descriptor(descriptor) for descriptor in descriptors]

	def mkClassLevel(self, classlevel):
		return self.session.query(ClassLevel).filter(ClassLevel.d20class == classlevel.d20class, ClassLevel.level == classlevel.level).first() or ClassLevel(classlevel.d20class, classlevel.level)

	def addSpell(self, spell):
		spell.descriptors = self.mkDescriptors([descriptor.descriptor for descriptor in spell.descriptors])
		spell.classlevels = [self.mkClassLevel(cl) for cl in spell.classlevels]
		self.session.add(spell)
#		self.session.flush()
#		self.session.commit()




