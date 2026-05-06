import logging
import os
import os.path as osp

import pandas as pd

from src.preprocessing import readinuser, preprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

data_directory: str = osp.join(osp.curdir, "data")
users: list[str] = ["User1", "User2"]

logger.info(
    f"Starting preprocessing for {len(users)} users from directory: {data_directory}"
)

for user in users:
    # Get the directory of the current user
    user_directory: str = osp.join(data_directory, user)
    logger.info(f"Processing user: {user}")

    # Get the paths to the recordings of single days available for current user
    user_days: list[str] = [
        path
        for path in os.listdir(user_directory)
        if osp.isdir(osp.join(user_directory, path))
    ]
    logger.info(f"Found {len(user_days)} days of recordings: {sorted(user_days)}")

    # Read the data for each day as a dataframe
    data: list[pd.DataFrame] = []
    for day in sorted(user_days):
        day_path = osp.join(user_directory, day)
        df_day = readinuser(day_path)
        data.append(df_day)
        logger.debug(f"  Loaded day {day}: {len(df_day)} records")

    # Join dataframes of all days
    logger.info(f"Concatenating data from {len(data)} days...")
    df: pd.DataFrame = pd.concat(data)
    logger.info(f"Total records after concatenation: {len(df)}")

    # remove unneccessary columns
    logger.info("Removing unnecessary columns: time_ms_x, time_ms_y")
    df = df.drop(columns=["time_ms_x", "time_ms_y"])

    logger.info("Preprocessing data...")
    gdf = preprocess(df, osp.join(user_directory, "trip_times.csv"))

    # Save the joined dataframe as a csv
    output_path = osp.join(user_directory, "data.csv")
    gdf.to_csv(output_path, index=False, encoding="utf8")
    logger.info(f"Saved processed data to: {output_path}")
    gdf.to_pickle(osp.join(user_directory, "data.pkl"))
    logger.info(f"Completed processing for user {user}\n")

logger.info("Preprocessing complete for all users!")
