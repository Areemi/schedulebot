import logging
from itertools import product
from pathlib import Path

import click
import pandas as pd

from schedulebot.db.client import DatabaseClient
from schedulebot.db.models import (
    Group,
    GroupSubject,
    Qualification,
    Room,
    RoomType,
    StudyInterval,
    Subject,
    SubjectRoom,
    Teacher,
    TeacherSubject,
    TimeInterval,
    Weekdays,
)
from schedulebot.utils.load import (
    get_days,
    get_groups,
    get_time_intervals,
    room_type_map,
    room_types,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("database_loading")

PROJECT_DPATH = Path(__file__).parent.parent.resolve()
DATA_DPATH = PROJECT_DPATH / "data"


def add_qualifications(df: pd.DataFrame, db_client: DatabaseClient):
    qualifications = df["TEACHERS"].str.split().str[-1].unique()
    qualification_df = pd.Series(qualifications, name="name")
    db_client.add_df(df=qualification_df, table_name=Qualification.__tablename__)


def add_days(db_client: DatabaseClient):
    weekdays_ds = pd.Series(get_days(), name="name")
    db_client.add_df(df=weekdays_ds, table_name=Weekdays.__tablename__)


def add_time_intervals(db_client: DatabaseClient):
    time_interval_ds = pd.Series(get_time_intervals(), name="interval")
    db_client.add_df(df=time_interval_ds, table_name=TimeInterval.__tablename__)


def add_study_intervals(db_client: DatabaseClient):
    study_days = db_client.get_id_list(Weekdays)
    time_interval = db_client.get_id_list(TimeInterval)

    time_slot_ids = list(product(study_days, time_interval))
    for day_id, time_slot_id in time_slot_ids:
        record = StudyInterval(time_interval_id=time_slot_id, day_id=day_id)
        db_client.add_record(record)


def add_teachers(df: pd.DataFrame, db_client: DatabaseClient):
    full_teachers_names = df["TEACHERS"].tolist()
    lessons_one_week = df["TEACHERS_LESSONS_ONE_WEEK"].tolist()

    for teacher_info, teacher_load in zip(full_teachers_names, lessons_one_week):
        middle_name, first_name, last_name, qualification = teacher_info.split()
        quality_id = db_client.get_id(Qualification, [Qualification.name.like(qualification)])
        record = Teacher(middle_name=middle_name,
                         first_name=first_name,
                         last_name=last_name,
                         qualification_id=quality_id,
                         load_hours=teacher_load)
        db_client.add_record(record)


def add_subjects(df: pd.DataFrame, db_client: DatabaseClient):
    subject_ds = pd.Series(df["subjects"], name="name")
    db_client.add_df(subject_ds, table_name=Subject.__tablename__)


def add_teacher_subject(df: pd.DataFrame, db_client: DatabaseClient):
    subjects_info = df["subjects"].values
    teachers_info = df.apply(lambda row: row[row == 1].index.values, axis=1).values

    for list_names, subject in zip(teachers_info, subjects_info):
        subject_index = db_client.get_id(Subject, [Subject.name.like(subject)])
        for name in list_names:
            middle_name, first_name, last_name = name.split()[:-1]
            conditions = [
                Teacher.first_name.like(first_name),
                Teacher.middle_name.like(middle_name),
                Teacher.last_name.like(last_name)
            ]
            teacher_index = db_client.get_id(Teacher, conditions)
            record = TeacherSubject(teacher_id=teacher_index, subject_id=subject_index)
            db_client.add_record(record)


def add_room_type(db_client: DatabaseClient):
    room_ds = pd.Series(room_types(), name="name")
    db_client.add_df(df=room_ds, table_name=RoomType.__tablename__)


def add_rooms(df: pd.DataFrame, db_client: DatabaseClient):
    room_types_map = room_type_map()
    for room, subject_type in zip(df["room"], df["subject_type"]):
        building, floor = room[:2]
        number = room[2:]
        subject_type = room_types_map[subject_type]
        type_id = db_client.get_id(RoomType, [RoomType.name.like(subject_type)])
        record = Room(
            name=room,
            building=building,
            floor=floor,
            number=number,
            type_id=type_id
        )
        db_client.add_record(record)


def add_subject_room(df: pd.DataFrame, db_client: DatabaseClient, subjects: list[str]):
    labs = df["lab"]
    rooms = df["room"]
    for x, lab in zip(rooms, labs):
        room_id = db_client.get_id(Room, conditions=[Room.name.like(x)])
        lab = lab + " лаб."
        subject_id = db_client.get_id(Subject, conditions=[Subject.name.like(lab)])
        record = SubjectRoom(subject_id=subject_id, room_id=room_id)
        db_client.add_record(record)

    mixed_id = db_client.get_id(RoomType, conditions=[RoomType.name.like("mixed")])
    mixed_room_id = db_client.get_filter_ids(Room, conditions=[Room.type_id.like(mixed_id)])
    for subject_type in subjects:
        subject_id = db_client.get_id(Subject, conditions=[Subject.name.like(subject_type)])
        subject_type = subject_type.split()[-1]
        if subject_type != "лаб.":
            room_type = room_type_map()[subject_type]
            type_id = db_client.get_id(RoomType, [RoomType.name.like(room_type)])
            rooms_id = db_client.get_filter_ids(Room, conditions=[Room.type_id.like(type_id)])
            for room_id in rooms_id:
                record = SubjectRoom(subject_id=subject_id, room_id=room_id)
                db_client.add_record(record)

            for id in mixed_room_id:
                record = SubjectRoom(subject_id=subject_id, room_id=id)
                db_client.add_record(record)


def add_groups(db_client: DatabaseClient):
    groups = pd.Series(get_groups(), name="name")
    db_client.add_df(groups, table_name=Group.__tablename__)


def add_group_subject(df: pd.DataFrame, db_client: DatabaseClient):
    subjects = df["subjects"].values
    groups_info = df.apply(lambda row: row[row == 1].index.values, axis=1).values
    for subject, group_list in zip(subjects, groups_info):
        subject_id = db_client.get_id(Subject, conditions=[Subject.name.like(subject)])
        for value in group_list:
            group_id = db_client.get_id(Group, conditions=[Group.name.like(int(value))])
            record = GroupSubject(group_id=group_id, subject_id=subject_id)
            db_client.add_record(record)


@click.command()
@click.option("-v", "--data-version", required=True, help="The name of the data folder.")
def main(data_version: str):
    src_data_dpath = DATA_DPATH / data_version

    db_client = DatabaseClient()

    teacher_subject_df = pd.read_csv(src_data_dpath / "Teachers+Lessons.csv")

    add_qualifications(teacher_subject_df, db_client)
    logger.debug("Qualifications were stored successfully")

    add_teachers(teacher_subject_df, db_client)
    logger.debug("Teachers information was stored successfully")

    add_days(db_client)
    logger.debug("Days were stores successfully")

    add_time_intervals(db_client)
    logger.debug("Time intervals were stored successfully")

    add_study_intervals(db_client)
    logger.debug("Study Intervals were stored successfully")

    add_room_type(db_client)
    logger.debug("Room types were stored successfully")
    add_groups(db_client)
    logger.debug("Groups information was stored successfully")

    subject_teacher_df = pd.read_csv(src_data_dpath / "Subjects+Teachers.csv", index_col=0)
    add_subjects(subject_teacher_df, db_client)
    logger.debug("Subjects were stored successfully")
    add_teacher_subject(subject_teacher_df, db_client)
    logger.debug("Teacher-Subjects were stored successfully")

    room_df = pd.read_csv(src_data_dpath / "Room+Subject_Type.csv", index_col=0)
    add_rooms(room_df, db_client)
    logger.debug("Rooms were stored successfully")

    subject_room_df = pd.read_csv(src_data_dpath / "Lab+Room.csv", index_col=0)
    add_subject_room(subject_room_df, db_client, subject_teacher_df["subjects"])
    logger.debug("Subject-Rooms were stored successfully")

    subject_group_df = pd.read_csv(src_data_dpath / "Subjects+Groups.csv", index_col=0)
    add_group_subject(subject_group_df, db_client)
    logger.debug("Subject-Groups were stored successfully")


if __name__ == "__main__":
    main()
