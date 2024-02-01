from sqlalchemy import Column, Float, ForeignKey, Integer, MetaData, String
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
Model = declarative_base(metadata=metadata)


class Qualification(Model):
    """Table with values/types qualification"""

    __tablename__ = "qualification"

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[str] = Column(String(30), nullable=False)

    def __repr__(self):
        return(f"<Qualification(id={self.id}, name={self.name})>")


class Weekdays(Model):
    """Table with the days from Monday to Saturday"""

    __tablename__ = "weekday"

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[str] = Column(String(30), nullable=False)


class TimeInterval(Model):
    """Table with time intervals"""

    __tablename__ = "time_interval"

    id: Column[int] = Column(Integer, primary_key=True)
    interval: Column[str] = Column(String(30), nullable=False)


class StudyInterval(Model):
    """Table with study interval"""

    __tablename__ = "study_interval"

    id: Column[int] = Column(Integer, primary_key=True)
    time_interval_id: Column[int] = Column(ForeignKey('time_interval.id'))
    day_id: Column[int] = Column(ForeignKey('weekday.id'))


class Teacher(Model):
    """Table with names of teachers and load hours"""

    __tablename__ = "teachers"

    id: Column[int] = Column(Integer, primary_key=True)
    middle_name: Column[str] = Column(String(30), nullable=False)
    first_name: Column[str] = Column(String(30), nullable=False)
    last_name: Column[str] = Column(String(30), nullable=False)
    load_hours: Column[float] = Column(Float, nullable=False)
    qualification_id: Column[int] = Column(ForeignKey('qualification.id'))
    # TODO: add department name (-> add department table)


class Subject(Model):
    """Table with subjects"""

    __tablename__ = "subjects"

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[str] = Column(String(30), nullable=False)


class TeacherSubject(Model):
    """Table with teachers subjects"""

    __tablename__ = "teachers_subjects"

    id: Column[int] = Column(Integer, primary_key=True)
    teacher_id: Column[int] = Column(ForeignKey("teachers.id"))
    subject_id: Column[int] = Column(ForeignKey("subjects.id"))


class RoomType(Model):
    """Table with room type"""

    __tablename__ = "room_type"

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[str] = Column(String(30), nullable=False)


class Room(Model):
    """Table with university's rooms"""

    __tablename__ = "room"

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[str] = Column(String, nullable=False)
    building: Column[str] = Column(String, nullable=False)
    floor: Column[int] = Column(Integer, nullable=False)
    number: Column[str] = Column(String, nullable=False)
    type_id: Column[int] = Column(ForeignKey("room_type.id"))


class SubjectRoom(Model):
    """Table with university's subject rooms"""

    __tablename__ = "subject_room"

    id: Column[int] = Column(Integer, primary_key=True)
    subject_id: Column[int] = Column(ForeignKey('subjects.id'))
    room_id: Column[int] = Column(ForeignKey('room.id'))


class Group(Model):
    """Table with groups"""

    __tablename__ = 'group'

    id: Column[int] = Column(Integer, primary_key=True)
    name: Column[int] = Column(Integer, nullable=False)


class GroupSubject(Model):
    """Table with groups and subjects"""

    __tablename__ = 'group_subject'

    id: Column[int] = Column(Integer, primary_key=True)
    group_id: Column[int] = Column(ForeignKey('group.id'))
    subject_id: Column[int] = Column(ForeignKey('subjects.id'))
