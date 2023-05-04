import logging
import os

import click
import numpy as np
import pandas as pd

from schedulebot.db.client import DatabaseClient
from schedulebot.db.models import Qualification, Study_interval, Teacher, Time_interval, Weekdays
from schedulebot.utils.data import parse_subject_name
from schedulebot.utils.load import get_time_intervals, weekdays

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database_loading")
CURRENT_DPATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DPATH, os.pardir))
DATA_DPATH = os.path.join(PROJECT_ROOT, "data")


@click.command()
@click.option("--version", required=True, help="The name of the data folder.")
def main(version: str):
    data_version = version
    src_dpath = os.path.join(DATA_DPATH, data_version)
    fpath = os.path.join(src_dpath, "Teachers+Lessons.csv")
    dataframe = pd.read_csv(fpath)

    parsed_teachers_name = dataframe['TEACHERS'].apply(parse_subject_name).tolist()
    parsed_teachers_name = np.array(parsed_teachers_name).reshape(-1, 2)

    dataframe['qualification'] = parsed_teachers_name[:, 1]

    db_client = DatabaseClient()

    # --- Qualification --- #
    qualification_df = pd.DataFrame(dataframe['qualification'].unique(), columns=['name'])
    db_client.add_df(df=qualification_df, table_name=Qualification.__tablename__)

    # --- Days --- #
    weekdays_ds = pd.Series(weekdays(), name="name")
    db_client.add_df(df=weekdays_ds, table_name=Weekdays.__tablename__)

    # --- Time interval --- #
    time_interval_df = pd.DataFrame(get_time_intervals(), columns=['interval'])
    db_client.add_df(df=time_interval_df, table_name=Time_interval.__tablename__)

    # --- Study interval --- #
    studydays = db_client.get_id_list(Weekdays)
    studytime = db_client.get_id_list(Time_interval)
    for day in studydays:
        for time in studytime:
            record = Study_interval(time_interval_id=time, day_id=day)
            db_client.add_record(record)

    # --- Teachers --- #
    full_teachers_names = dataframe['TEACHERS'].tolist()
    lessons_one_week = dataframe['TEACHERS_LESSONS_ONE_WEEK'].tolist()

    for teacher_info, teacher_load in zip(full_teachers_names, lessons_one_week):
        last_name, first_name, middle_name, qualification = teacher_info.split()
        record = Teacher(middle_name=middle_name,
                         first_name=first_name,
                         last_name=last_name,
                         qualification_id=db_client.get_id(Qualification,
                                                           Qualification.name,
                                                           qualification)[0],
                         load_hours=teacher_load)
        db_client.add_record(record)


if __name__ == "__main__":
    main()
