import logging

from sqlalchemy import Engine, text
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, create_engine, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.config import settings
from app.core.db import test_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


def ensure_test_database_exists() -> None:
    """Create the test database if it doesn't exist."""
    # Connect to postgres database to create the test database
    postgres_uri = str(settings.SQLALCHEMY_DATABASE_URI).rsplit("/", 1)[0] + "/postgres"
    postgres_engine = create_engine(postgres_uri, isolation_level="AUTOCOMMIT")

    test_db_name = settings.POSTGRES_TEST_DB or f"{settings.POSTGRES_DB}_test"

    try:
        with Session(postgres_engine) as session:
            # Check if database exists
            result = session.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name").bindparams(
                    db_name=test_db_name
                )
            ).first()

            if not result:
                logger.info(f"Creating test database: {test_db_name}")
                session.execute(text(f'CREATE DATABASE "{test_db_name}"'))
                session.commit()
                logger.info(f"Test database {test_db_name} created successfully")
            else:
                logger.info(f"Test database {test_db_name} already exists")
    except OperationalError as e:
        logger.warning(f"Could not create test database (it may already exist): {e}")
    finally:
        postgres_engine.dispose()


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:
        # Try to create session to check if DB is awake
        with Session(db_engine) as session:
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing test service")
    # Ensure test database exists before checking connection
    ensure_test_database_exists()
    init(test_engine)
    logger.info("Test service finished initializing")


if __name__ == "__main__":
    main()
