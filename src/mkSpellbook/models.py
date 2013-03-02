from sqlalchemy import Column, Boolean, LargeBinary, Integer, String, create_engine, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()

descriptors_to_spells = Table('descriptors_to_spells', Base.metadata,
	Column('spell_id', Integer, ForeignKey('spells.id')),
	Column('descriptor_id', Integer, ForeignKey('descriptors.id')))


classlevels_to_spells = Table("classlevels_to_spells", Base.metadata,
	Column('spell_id', Integer, ForeignKey('spells.id')),
	Column('classlevel_id', Integer, ForeignKey('classlevels.id')))

spellbooks_to_spellswithclasslevels = Table("spellbooks_to_spellswithclasslevels", Base.metadata,
	Column("spellbooks_id", Integer, ForeignKey("spellbooks.id")),
	Column("spellswithclasslevels_id", Integer, ForeignKey("spells_with_classlevels.id")))

class SpellWithClasslevel(Base):
	__tablename__ = "spells_with_classlevels"
	id = Column(Integer, primary_key = True)
	spell_id = Column(Integer, ForeignKey('spells.id'))
	classlevel_id = Column(Integer, ForeignKey('classlevels.id'))
	classlevel = relationship("ClassLevel", backref="cl2s")
	spell = relationship("Spell", backref="s2cl")


class Descriptor(Base):
	__tablename__ = "descriptors"
	id = Column(Integer, primary_key = True)
	descriptor = Column(String, unique=True)
	def __init__(self, descriptor):
		self.descriptor = descriptor

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
	classlevels = association_proxy("s2cl", "classlevel")
	

class ClassLevel(Base):
	__tablename__ = "classlevels"
	id = Column(Integer, primary_key = True)
	d20class = Column(String)
	level = Column(Integer)
	spells = association_proxy("cl2s", "spell")
	__table_args__ = (UniqueConstraint(d20class, level), )
	def __init__(self, d20class, level):
		self.d20class = d20class
		self.level = level
	
class Spellbook(Base):
	__tablename__ = "spellbooks"
	id = Column(Integer, primary_key = True)
	author = Column(String)
	name = Column(String, unique = True)
	author = Column(String)
	logo = Column(LargeBinary)
	logoext = Column(String)
	spells = relationship("SpellWithClasslevel", secondary=spellbooks_to_spellswithclasslevels)


