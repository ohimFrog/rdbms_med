from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Manufacturer(Base):
    __tablename__ = 'manufacturer'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    
    drugs = relationship("DrugBasic", back_populates="manufacturer")

class DrugBasic(Base):
    __tablename__ = 'drug_basic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
    storage = Column(Text)
    
    manufacturer = relationship("Manufacturer", back_populates="drugs")
    usage = relationship("DrugUsage", uselist=False, back_populates="drug")
    warning = relationship("DrugWarning", uselist=False, back_populates="drug")
    side_effect = relationship("DrugSideEffect", uselist=False, back_populates="drug")

class DrugUsage(Base):
    __tablename__ = 'drug_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_id = Column(Integer, ForeignKey('drug_basic.id'), unique=True)
    effect = Column(Text)
    dosage = Column(Text)
    
    drug = relationship("DrugBasic", back_populates="usage")

class DrugWarning(Base):
    __tablename__ = 'drug_warning'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_id = Column(Integer, ForeignKey('drug_basic.id'), unique=True)
    precaution = Column(Text)
    interaction = Column(Text)
    
    drug = relationship("DrugBasic", back_populates="warning")

class DrugSideEffect(Base):
    __tablename__ = 'drug_side_effect'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    drug_id = Column(Integer, ForeignKey('drug_basic.id'), unique=True)
    side_effect = Column(Text)
    
    drug = relationship("DrugBasic", back_populates="side_effect")
