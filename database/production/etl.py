from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from database.production.models import Organisations
from database.production.mappings import MAPPINGS

import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('postgresql://username:password@localhost:5432/production_db', echo=False)
Session = sessionmaker(bind=engine)

def extract_data():
    """Simulate extraction of data from web scraping/API."""
    return [
        {
            'name': 'Community Group A',
            'established_date': '2020-01-15',
            'description_text': 'A community organization focused on education.',
            'public_status': True,
            'slug_value': 'community-group-a',
            'inserted_by_id': '123e4567-e89b-12d3-a456-426614174000',
            'last_edited_by_id': '123e4567-e89b-12d3-a456-426614174000'
        },
        {
            'name': 'Charity B',
            'established_date': None,
            'description_text': None,
            'public_status': False,
            'slug_value': 'charity-b',
            'inserted_by_id': None,
            'last_edited_by_id': None
        }
    ]

def transform_data(source_data, mappings):
    """Transform source data according to mappings."""
    transformed = []
    for record in source_data:
        transformed_record = {}
        org_mapping = mappings['organisations']
        for src_field, config in org_mapping['source_fields'].items():
            value = record.get(src_field)
            if value is not None:
                try:
                    transformed_record[config['target']] = config['transform'](value)
                except Exception as e:
                    logger.error(f"Error transforming field {src_field}: {str(e)}")
                    transformed_record[config['target']] = None
            elif config['target'] not in transformed_record:
                transformed_record[config['target']] = None
        for field, default_fn in org_mapping['defaults'].items():
            transformed_record[field] = default_fn()
        transformed.append(transformed_record)
    return transformed

def load_data(transformed_data):
    """Load transformed data into the database."""
    session = Session()
    try:
        for record in transformed_data:
            # Check for existing organisation by slug
            existing_org = session.query(Organisations).filter_by(slug=record['slug']).first()
            if existing_org:
                logger.info(f"Updating existing organisation: {existing_org.slug}")
                for key, value in record.items():
                    if value is not None:
                        setattr(existing_org, key, value)
            else:
                org = Organisations(**record)
                session.add(org)
                logger.info(f"Adding new organisation: {record['slug']}")
        session.commit()
        logger.info("Data loaded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error loading data: {str(e)}")
        raise
    finally:
        session.close()

def run_etl():
    """Run the ETL pipeline."""
    try:
        logger.info("Starting extraction...")
        source_data = extract_data()
        logger.info(f"Extracted {len(source_data)} records.")
        logger.info("Starting transformation...")
        transformed_data = transform_data(source_data, MAPPINGS)
        logger.info(f"Transformed {len(transformed_data)} records.")
        logger.info("Starting load...")
        load_data(transformed_data)
        logger.info("ETL completed successfully.")
    except Exception as e:
        logger.error(f"ETL failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Enable uuid-ossp extension
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
    # Create tables in the specified schema
    Base.metadata.create_all(engine)
    run_etl()