from dotenv import load_dotenv
import logging
import os


def init_onefile():
    # Load environment variables
    load_dotenv()

    # Set up logging
    log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
