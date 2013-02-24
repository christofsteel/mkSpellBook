from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:////home/christoph/sqlitestest.db', echo=True)
Session = sessionmaker(bind=engine)


descriptors_to_uSpells = Table('descriptors_to_uSpells', Base.metadata,
	Column('uSpells_id', Integer, ForeignKey('unique_spells.id')),
	Column('descriptor_id', Integer, ForeignKey('descriptors.id')))

class Descriptor(Base):
	__tablename__ = "descriptors"
	id = Column(Integer, primary_key = True)
	descriptor = Column(String)

class Unique_Spell(Base):
	__tablename__ = "unique_spells"
	id = Column(Integer, primary_key = True)
	ruleset = Column(String)
	link = Column(String)
	name = Column(String)
	book = Column(String)
	edition = Column(String)
	school = Column(String)
	subschool = Column(String)
	verbal = Column(Integer)
	somatic = Column(Integer)
	material = Column(Integer)
	arcanefocus = Column(Integer)
	divinefocus = Column(Integer)
	xpcost = Column(Integer)
	castingtime = Column(String)
	spellrange = Column(String)
	area = Column(String)
	target = Column(String)
	duration = Column(String)
	savingthrow = Column(String)
	spellres = Column(String)
	spelltext = Column(String)
	descriptors = relationship("Descriptor", secondary=descriptors_to_uSpells)

class ClassLevel(Base):
	__tablename__ = "classlevels"
	id = Column(Integer, primary_key = True)
	d20class = Column(String)
	level = Column(Integer)


class Spell(Base):
	__tablename__ = "spells"
	id = Column(Integer, primary_key = True)
	uSpells_id = Column(Integer, ForeignKey('unique_spells.id'))
	uSpell = relationship("Unique_Spell")
	classlevels_id = Column(Integer, ForeignKey('classlevels.id'))
	classlevel = relationship("ClassLevel")
	d20class = classlevel.d20class
