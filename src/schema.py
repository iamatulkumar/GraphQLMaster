import asyncio
from asyncio import Queue
from typing import List, AsyncGenerator
import strawberry
from typing_extensions import Optional

from .models import College, Student
from .database import get_db


@strawberry.type
class CollegeType:
    id: int
    name: str
    location: str
    established_year: str
    profile_url: str


@strawberry.type
class StudentType:
    id: int
    name: str
    dob: str
    college_id: int
    profile_url: str
    gender: str


@strawberry.type
class PaginationCollegeType:
    total: int
    limit: int
    size: int
    next_page: Optional[int]
    colleges: List[CollegeType]


@strawberry.type
class ResponseType:
    message: str


@strawberry.type
class Query:
    @strawberry.field
    async def colleges(self) -> List[CollegeType]:
        db = get_db()
        colleges = db.query(College).all()
        return [CollegeType(id=college.id, name=college.name, location=college.location,
                            established_year=college.established_year, profile_url=college.profile_url) for college in
                colleges]

    @strawberry.field
    async def pagination_colleges(self, skip: int = 0, limit: int = 5) -> PaginationCollegeType:
        db = get_db()
        colleges = db.query(College).offset(skip).limit(limit).all()

        collegesTypeList = [CollegeType(id=college.id, name=college.name, location=college.location,
                                        established_year=college.established_year,
                                        profile_url=college.profile_url) for college in colleges]

        count = db.query(College).count()
        next_page = skip + limit

        return PaginationCollegeType(total=count, limit=limit, size=skip, next_page=next_page,
                                     colleges=collegesTypeList)

    @strawberry.field
    async def college_by_id(self, college_id: int) -> CollegeType:
        db = get_db()
        college = db.query(College).filter(College.id == college_id).first()
        return CollegeType(id=college.id, name=college.name, location=college.location,
                           established_year=college.established_year, profile_url=college.profile_url)

    @strawberry.field
    async def students(self) -> List[StudentType]:
        db = get_db()
        students = db.query(Student).all()
        return [StudentType(id=student.id, name=student.name, dob=student.dob, gender=student.gender,
                            profile_url=student.profile_url, college_id=student.college_id, ) for
                student in students]

    @strawberry.field
    async def student_by_id(self, student_id: int) -> StudentType:
        db = get_db()
        student = db.query(Student).filter(Student.id == student_id).first()
        return StudentType(id=student.id, name=student.name, dob=student.dob, gender=student.gender,
                           profile_url=student.profile_url, college_id=student.college_id)

    @strawberry.field
    async def students_by_college_id(self, college_id: int) -> List[StudentType]:
        db = get_db()
        students = db.query(Student).filter(Student.college_id == college_id).first()
        return [StudentType(id=student.id, name=student.name, dob=student.dob, gender=student.gender,
                            profile_url=student.profile_url, college_id=student.college_id, ) for
                student in students]


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_college(self, name: str, location: str, established_year: str) -> CollegeType:
        db = get_db()
        college = College(name=name, location=location, established_year=established_year)
        db.add(college)
        db.commit()
        db.refresh(college)
        return CollegeType(id=college.id, name=college.name, location=college.location,
                           established_year=college.established_year, profile_url=college.profile_url)

    @strawberry.mutation
    async def delete_college(self, college_id: int) -> ResponseType:
        db = get_db()
        college = db.query(College).filter(College.id == college_id).first()
        if not college:
            raise ValueError("College not found")
        db.delete(college)
        db.commit()
        return ResponseType(message="College deleted successfully")

    @strawberry.mutation
    async def create_student(self, name: str, dob: str, gender: str, profile_url: str, college_id: int) -> StudentType:
        db = get_db()
        college = db.query(College).filter(College.id == college_id).first()
        if not college:
            raise ValueError("College not found")
        student = Student(name=name, dob=dob, college_id=college_id, profile_url=profile_url, gender=gender)
        db.add(student)
        db.commit()
        db.refresh(student)
        await message_queue.put(student)
        return StudentType(id=student.id, name=student.name, dob=student.dob, college_id=student.college_id,
                           profile_url=student.profile_url, gender=student.gender)

    @strawberry.mutation
    async def delete_student(self, student_id: int) -> ResponseType:
        db = get_db()
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("Student not found")
        db.delete(student)
        db.commit()
        return ResponseType(message="College deleted successfully")


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def student_added(self, college_id: int) -> StudentType:
        async for student in student_stream(college_id):
            yield student


message_queue = Queue()


async def student_stream(college_id: int) -> AsyncGenerator[StudentType, None]:
    while True:
        await asyncio.sleep(1)
        message = await message_queue.get()
        if message.college_id == college_id:
            yield StudentType(id=message.id, name=message.name, dob=message.dob, college_id=message.college_id,
                              profile_url=message.profile_url, gender=message.gender)


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
