from utils import logger
import json
import configparser
config = configparser.ConfigParser()
config.read('config.ini')
def create_raw_table(conn):
    """Creates a table to store raw JSON data if it doesn't exist."""
    sql_create_schema = "CREATE SCHEMA IF NOT EXISTS raw;"
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            raw_data JSONB,
            channel_name VARCHAR(22)
        );
    """
    try:
        cur = conn.cursor()
        cur.execute(sql_create_schema)
        cur.execute(sql_create_table)
        conn.commit()
        logger.info("Raw table created or already exists.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating raw table: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()

def load_raw_json(conn, file_path):
    """Loads a single raw JSON file into the raw table."""
    try:
        with open(file_path, 'r') as f:
            raw_json = f.read()
        channel_name = file_path.split('/')[-1].split('.')[0]
        cur = conn.cursor()
        sql_insert = "INSERT INTO raw.telegram_messages (raw_data, channel_name) VALUES (%s, %s);"
        cur.execute(sql_insert, (raw_json, channel_name,))
        conn.commit()
        logger.info(f"Successfully loaded {file_path} into raw table.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error loading {file_path}: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()