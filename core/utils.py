import logging
import os

def setup_logger():
    os.makedirs("reports/logs", exist_ok=True)
    logging.basicConfig(
        filename="reports/logs/framework.log",
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO,
    )
    return logging.getLogger("FrameworkLogger")
