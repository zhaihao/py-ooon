from pydantic import BaseModel, Field

from src.ooon.models_ext import JsonPathModel


def test_1():
    class User(BaseModel):
        id: int
        name: str
        age: int = Field(exclude=True)

    u = User(id=1, name='test', age=18)
    print(u.model_dump_json())
    print(u.model_dump())


def test_2():
    class User(JsonPathModel):
        id: int
        name: str
        age: int = Field(serializer=lambda x: x + 1)

    u = User(id=1, name='test', age=18)
    print(u)
    print(u.model_dump_json())
    print(u.model_dump())


def test_3():
    class User(JsonPathModel):
        id: int
        name: str = Field(serializer=lambda x: x.upper())
        age: int

    class A(JsonPathModel):
        u: User
        ul: list[User]

    a = A(u=User(id=1, name='test', age=18),
      ul=[User(id=2, name='test2', age=28),
          User(id=3, name='test3', age=38)]
      )
    print()
    print(a)
    print(a.model_dump())
    print(a.model_dump_json())
