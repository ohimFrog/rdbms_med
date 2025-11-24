import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, Manufacturer, DrugBasic, DrugUsage, DrugWarning, DrugSideEffect

load_dotenv()

db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

def init_db():
    print("Dropping tables...")
    Base.metadata.drop_all(engine)
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created.")

    csv_path = "data/drug_data_full.csv"
    if not os.path.exists(csv_path):
        print(f"CSV file not found at {csv_path}")
        return

    print("Reading CSV...")
    df = pd.read_csv(csv_path)
    # Fill NaN with empty string to avoid DB errors
    df = df.fillna("")

    print(f"Importing {len(df)} records...")
    
    for _, row in df.iterrows():
        # 1. Manufacturer
        m_name = row['cname'].strip()
        manufacturer = session.query(Manufacturer).filter_by(name=m_name).first()
        if not manufacturer:
            manufacturer = Manufacturer(name=m_name)
            session.add(manufacturer)
            session.flush() # Get ID
        
        # 2. DrugBasic
        drug = DrugBasic(
            name=row['pname'],
            manufacturer_id=manufacturer.id,
            storage=row['storage']
        )
        session.add(drug)
        session.flush() # Get ID
        
        # 3. DrugUsage
        usage = DrugUsage(
            drug_id=drug.id,
            effect=row['effect'],
            dosage=row['dosage']
        )
        session.add(usage)
        
        # 4. DrugWarning
        warning = DrugWarning(
            drug_id=drug.id,
            precaution=row['dprecaution'],
            interaction=row['interaction']
        )
        session.add(warning)
        
        # 5. DrugSideEffect
        side_effect = DrugSideEffect(
            drug_id=drug.id,
            side_effect=row['side_effect']
        )
        session.add(side_effect)
    
    session.commit()
    print("Data import completed.")

if __name__ == "__main__":
    init_db()
