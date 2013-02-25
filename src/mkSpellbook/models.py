from sqlalchemy import Column, Boolean, LargeBinary, Integer, String, create_engine, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

descriptors_to_spells = Table('descriptors_to_spells', Base.metadata,
	Column('spell_id', Integer, ForeignKey('spells.id')),
	Column('descriptor_id', Integer, ForeignKey('descriptors.id')))


classlevels_to_spells = Table("classlevels_to_spells", Base.metadata,
	Column('spell_id', Integer, ForeignKey('spells.id')),
	Column('classlevel_id', Integer, ForeignKey('classlevels.id')))

spellbooks_to_spellinspellbook = Table("spellbooks_to_spellinspellbook", Base.metadata,
	Column("spellbooks_id", Integer, ForeignKey("spellbooks.id")),
	Column("spellsinspellbook_id", Integer, ForeignKey("spell_in_spellbook.id")))

class SpellInSpellbook(Base):
	__tablename__ = "spell_in_spellbook"
	id = Column(Integer, primary_key = True)
	spell_id = Column(Integer, ForeignKey('spells.id'))
	spell = relationship("Spell")
	classlevel_id = Column(Integer, ForeignKey('classlevels.id'))
	classlevel = relationship("ClassLevel")


class Descriptor(Base):
	__tablename__ = "descriptors"
	id = Column(Integer, primary_key = True)
	descriptor = Column(String, unique=True)
	def __init__(self, descriptor):
		self.descriptor = descriptor
"""	def __eq__(self, other):
		return isinstance(other, Descriptor) and \
				other.descriptor == self.descriptor
"""

class Spell(Base):
	__tablename__ = "spells"
	id = Column(Integer, primary_key = True)
	ruleset = Column(String)
	link = Column(String)
	name = Column(String)
	book = Column(String)
	edition = Column(String)
	school = Column(String)
	subschool = Column(String)
	verbal = Column(Boolean)
	somatic = Column(Boolean)
	material = Column(Boolean)
	arcanefocus = Column(Boolean)
	divinefocus = Column(Boolean)
	xpcost = Column(Boolean)
	castingtime = Column(String)
	spellrange = Column(String)
	area = Column(String)
	target = Column(String)
	duration = Column(String)
	savingthrow = Column(String)
	spellres = Column(String)
	spelltext = Column(String)
	descriptors = relationship("Descriptor", secondary=descriptors_to_spells, backref="spells")
	classlevels = relationship("ClassLevel", secondary=classlevels_to_spells, backref="spells")

class ClassLevel(Base):
	__tablename__ = "classlevels"
	id = Column(Integer, primary_key = True)
	d20class = Column(String)
	level = Column(Integer)
	__table_args__ = (UniqueConstraint(d20class, level), )
	def __init__(self, d20class, level):
		self.d20class = d20class
		self.level = level
	
"""	def __eq__(self, other):
		return isinstance(other, ClassLevel) and \
				other.d20class == self.d20class and \
				other.lebel == self.level
"""

class Spellbook(Base):
	__tablename__ = "spellbooks"
	id = Column(Integer, primary_key = True)
	author = Column(String)
	name = Column(String)
	author = Column(String)
	logo = Column(LargeBinary)
	logoext = Column(String)
	spells = relationship("SpellInSpellbook", secondary=spellbooks_to_spellinspellbook)


