import logging
import os

import click
import pandas as pd

from schedulebot.db.client import DatabaseClient
from schedulebot.db.models import (
    Qualification,
    Study_interval,
    Subject,
    Teacher,
    Teacher_subject,
    Time_interval,
    Weekdays,
)
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

    db_client = DatabaseClient()

    # --- Qualification --- #
    qualification_data = dataframe["TEACHERS"].str.split().str[-1].unique()
    qualification_df = pd.DataFrame(qualification_data, columns=['name'])
    db_client.add_df(df=qualification_df, table_name=Qualification.__tablename__)

    # --- Days --- #
    weekdays_ds = pd.Series(weekdays(), name="name")
    db_client.add_df(df=weekdays_ds, table_name=Weekdays.__tablename__)

    # --- Time interval --- #
    time_interval_df = pd.DataFrame(get_time_intervals(), columns=['interval'])
    db_client.add_df(df=time_interval_df, table_name=Time_interval.__tablename__)

    # --- Study interval --- #
    teachers = db_client.get_id_list(Weekdays)
    subjects = db_client.get_id_list(Time_interval)
    for day in teachers:
        for time in subjects:
            record = Study_interval(time_interval_id=time, day_id=day)
            db_client.add_record(record)

    # --- Teachers --- #
    full_teachers_names = dataframe['TEACHERS'].tolist()
    lessons_one_week = dataframe['TEACHERS_LESSONS_ONE_WEEK'].tolist()

    for teacher_info, teacher_load in zip(full_teachers_names, lessons_one_week):
        middle_name, first_name, last_name, qualification = teacher_info.split()
        quality_id = db_client.get_id(Qualification, Qualification.name, qualification)[0]
        record = Teacher(middle_name=middle_name,
                         first_name=first_name,
                         last_name=last_name,
                         qualification_id=quality_id,
                         load_hours=teacher_load)
        db_client.add_record(record)

    # --- Subject --- #
    fpath_sub = os.path.join(src_dpath, "Subjects+Teachers.csv")
    subject_df = pd.read_csv(fpath_sub)
    subject_ds = pd.Series(subject_df["subjects"], name="name")
    db_client.add_df(subject_ds, table_name=Subject.__tablename__)

    # --- Teacher subject --- #
    i = 0
    for column in subject_df:
        if column != 'Unnamed: 0' and column != 'subjects':
            j = 0
            for index in subject_df[column]:
                if index == 1:
                    teacher = column.split()
                    teacher_index = db_client.get(Teacher, teacher[1], teacher[0], teacher[2])[0]
                    subject = subject_df.iloc[j, 1]
                    subject_index = db_client.get_id(Subject, Subject.name, subject)[0]
                    record = Teacher_subject(teacher_id=teacher_index, subject_id=subject_index)
                    db_client.add_record(record)
                j += 1
        i += 1


if __name__ == "__main__":
    main()
