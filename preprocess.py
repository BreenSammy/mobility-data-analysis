import logging
import os
import os.path as osp
from pathlib import Path

import pandas as pd

from src.pipeline import UserProcessingPipeline
from src.data_manager import UserDataManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

data_directory: Path = Path("data")
users: list[str] = ["User1", "User2"]

logger.info(
    f"Starting preprocessing for {len(users)} users from directory: {data_directory}"
)

for user in users:
    pipeline = UserProcessingPipeline(
        data_manager=UserDataManager(
            user_id=user,
            raw_data_dir=data_directory / "raw",
            processed_data_dir=data_directory / "processed",
            results_dir=Path("results"),
        ),
        logger=logger,
        rerun_preprocessing=False,
    )
    pipeline.run()

logger.info("Preprocessing complete for all users!")
