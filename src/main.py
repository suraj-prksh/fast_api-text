from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
import databases
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./test.db"

# Create a FastAPI instance
app = FastAPI()

# Create a databases.Database instance
database = databases.Database(DATABASE_URL)

# Create a SQLAlchemy engine
metadata = MetaData()
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# Create a SQLAlchemy sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a SQLAlchemy model
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("name", String, index=True),
    Column("email", String, unique=True, index=True),
)

# Pydantic model for user creation
class UserCreate(BaseModel):
    name: str
    email: str

# Route to create a new user
@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    query = users.insert().values(name=user.name, email=user.email)
    last_record_id = await database.execute(query)
    return {"id": last_record_id, **user.dict()}

# Route to get a user by ID
@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
