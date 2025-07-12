import os
from subprocess import run, CalledProcessError
from dotenv import load_dotenv
import logging

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Extract database credentials from .env
DATABASE_URL = os.getenv("DATABASE_URL")
DB_TYPE = os.getenv("DB_TYPE", "mysql")  # Default to MySQL
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file.")

# Parse database credentials from DATABASE_URL
try:
    from urllib.parse import urlparse

    parsed_url = urlparse(DATABASE_URL)
    DB_USER = parsed_url.username
    DB_PASSWORD = parsed_url.password
    DB_HOST = parsed_url.hostname
    DB_PORT = parsed_url.port
    DB_NAME = parsed_url.path.lstrip("/")
except Exception as e:
    raise ValueError(f"Failed to parse DATABASE_URL: {e}")

def ask_confirmation(step_name):
    """Ask for confirmation before proceeding with a step."""
    while True:
        response = input(f"Do you want to proceed with {step_name}? (yes/no): ").strip().lower()
        if response in ["yes", "no"]:
            return response == "yes"
        print("Invalid input. Please enter 'yes' or 'no'.")

def backup_database():
    """Backup the database before applying migrations."""
    try:
        logging.info("Backing up the database...")
        # Define the backup file path in the `api` folder
        backup_folder = os.path.join(os.getcwd(), "api")
        os.makedirs(backup_folder, exist_ok=True)  # Ensure the folder exists
        backup_file = os.path.join(backup_folder, f"{DB_NAME}_backup.sql")
        logging.debug(f"Backup file path: {backup_file}")

        # Determine the backup command based on the database type
        if DB_TYPE == "mysql":
            command = [
                "mysqldump",
                "-u", DB_USER,
                f"-p{DB_PASSWORD}",
                "-h", DB_HOST,
                "-P", str(DB_PORT),
                DB_NAME,
                "--result-file", backup_file
            ]
        elif DB_TYPE == "postgresql":
            command = [
                "pg_dump",
                "-U", DB_USER,
                "-h", DB_HOST,
                "-p", str(DB_PORT),
                "-d", DB_NAME,
                "-f", backup_file
            ]
        else:
            raise ValueError(f"Unsupported database type: {DB_TYPE}")

        logging.debug(f"Running backup command: {' '.join(command)}")
        run(command, check=True)
        logging.info(f"Database backup completed successfully. Backup file: {backup_file}")
    except FileNotFoundError:
        logging.critical(f"The backup command for {DB_TYPE} was not found. Ensure the database client tools are installed and in your PATH.")
        raise
    except CalledProcessError as e:
        logging.error("Database backup failed. Aborting migration to ensure data safety.")
        raise e

def check_versions_folder():
    """Check if the Alembic versions folder is empty."""
    versions_folder = os.path.join(os.getcwd(), "alembic", "versions")
    if not os.path.exists(versions_folder):
        os.makedirs(versions_folder)
    return len(os.listdir(versions_folder)) == 0

def stamp_database():
    """Stamp the database with the current state if no migrations exist."""
    try:
        logging.info("Stamping the database with the current state...")
        run(["alembic", "stamp", "head"], check=True)
        logging.info("Database stamped successfully.")
    except CalledProcessError as e:
        logging.error("Failed to stamp the database.")
        raise e

def generate_migration():
    """Generate a new migration file."""
    migration_message = input("Enter migration message: ")
    try:
        logging.info("Generating migration...")
        run(["alembic", "revision", "--autogenerate", "-m", migration_message], check=True)
        logging.info("Migration file generated successfully.")
    except CalledProcessError as e:
        logging.error("No changes detected or an error occurred during migration generation.")
        raise e

def apply_migration():
    """Apply the migration to the database."""
    try:
        logging.info("Applying migration...")
        run(["alembic", "upgrade", "head"], check=True)
        logging.info("Migration applied successfully.")
    except CalledProcessError as e:
        logging.error("An error occurred while applying the migration. Rolling back changes...")
        rollback_migration()
        raise e

def rollback_migration():
    """Rollback the last migration in case of failure."""
    try:
        logging.info("Rolling back the last migration...")
        run(["alembic", "downgrade", "-1"], check=True)
        logging.info("Rollback completed successfully.")
    except CalledProcessError:
        logging.critical("Rollback failed. Please check the database manually.")

def run_migrations():
    """Run the full migration process."""
    try:
        # Step 1: Backup the database
        if ask_confirmation("backing up the database"):
            backup_database()
        else:
            logging.info("Skipping database backup.")

        # Step 2: Check if the versions folder is empty
        if check_versions_folder():
            logging.info("Alembic versions folder is empty.")
            if ask_confirmation("stamping the database with the current state"):
                stamp_database()
            else:
                logging.info("Skipping database stamping.")

        # Step 3: Generate a migration
        if ask_confirmation("generating a migration"):
            generate_migration()
        else:
            logging.info("Skipping migration generation.")

        # Step 4: Apply the migration
        if ask_confirmation("applying the migration"):
            apply_migration()
        else:
            logging.info("Skipping migration application.")

    except Exception as e:
        logging.error(f"Migration process failed: {e}")
        logging.info("Migration process terminated.")

if __name__ == "__main__":
    run_migrations()