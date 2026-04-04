from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
import uuid
from openai import OpenAI
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re

# AUTH
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


# LOAD ENV


load_dotenv()

# API USAGE

app = FastAPI(title="AI Notes API with Auth")


# ENV


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY missing")

if not MONGO_URI:
    raise Exception("MONGO_URI missing")


# OPENAI


client_ai = OpenAI(api_key=OPENAI_API_KEY)


# DATABASE


client_db = MongoClient(MONGO_URI)
db = client_db["notes_db"]

notes_collection = db["notes"]
users_collection = db["users"]

# Indexes
try:
    notes_collection.create_index("title")
    notes_collection.create_index("content")
    users_collection.create_index("username", unique=True)
except Exception as e:
    print("Index warning:", e)


# AUTH CONFIG


SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# MODELS


class Note(BaseModel):
    title: str
    content: str

    @field_validator("title", "content")
    @classmethod
    def not_empty(cls, value):
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value


class User(BaseModel):
    username: str
    password: str


# AUTH UTILS


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# AUTH ROUTES


# USER SIGNUP

@app.post("/signup")
def signup(user: User):
    existing = users_collection.find_one({"username": user.username})

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    users_collection.insert_one({
        "username": user.username,
        "password": hash_password(user.password)
    })

    return {"status": "success", "message": "User created"}


# USER LOGIN 

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = users_collection.find_one({"username": form_data.username})

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username")

    if not verify_password(form_data.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_access_token({"sub": form_data.username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# NOTES ROUTES 


# SEARCH NOTES BY QUERY

@app.get("/notes/search")
def search_notes(query: str, user: str = Depends(get_current_user)):
    safe_query = re.escape(query)

    results = list(notes_collection.find(
        {
            "owner": user,
            "$or": [
                {"title": {"$regex": safe_query, "$options": "i"}},
                {"content": {"$regex": safe_query, "$options": "i"}}
            ]
        },
        {"_id": 0}
    ))

    return {"status": "success", "data": results}


# CREATE NOTES

@app.post("/notes")
def create_note(note: Note, user: str = Depends(get_current_user)):
    try:
        print("USER:", user)  # debug

        new_note = {
            "id": str(uuid.uuid4()),
            "title": note.title,
            "content": note.content,
            "summary": None,
            "owner": user
        }

        result = notes_collection.insert_one(new_note)

        print("INSERTED ID:", result.inserted_id)  

        
        return {
            "status": "success",
            "data": {
                "id": new_note["id"],
                "title": new_note["title"],
                "content": new_note["content"],
                "summary": new_note["summary"],
                "owner": new_note["owner"]
            }
        }

    except Exception as e:
        print("CREATE NOTE ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# GET ALL NOTES

@app.get("/notes")
def get_notes(user: str = Depends(get_current_user)):
    notes = list(notes_collection.find({"owner": user}, {"_id": 0}))
    return {"status": "success", "data": notes}


# GET NOTES BY SPECIFIC NOTE ID 

@app.get("/notes/{note_id}")
def get_note(note_id: str, user: str = Depends(get_current_user)):
    note = notes_collection.find_one(
        {"id": note_id, "owner": user},
        {"_id": 0}
    )

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"status": "success", "data": note}


# UPDATE NOTES BY NOTE ID

@app.put("/notes/{note_id}")
def update_note(note_id: str, updated: Note, user: str = Depends(get_current_user)):
    result = notes_collection.update_one(
        {"id": note_id, "owner": user},
        {
            "$set": {
                "title": updated.title,
                "content": updated.content,
                "summary": None
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"status": "success", "message": "Updated"}


# DELETE NOTES BY NOTE ID

@app.delete("/notes/{note_id}")
def delete_note(note_id: str, user: str = Depends(get_current_user)):
    result = notes_collection.delete_one({"id": note_id, "owner": user})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")

    return {"status": "success", "message": "Deleted"}


# AI SUMMARY


def generate_summary(text: str):
    try:
        response = client_ai.responses.create(
            model="gpt-4o-mini",
            input=f"Summarize this in 2-3 lines:\n{text}"
        )
        return response.output_text
    except Exception:
        return text[:100] + "..."

# GENERATE SUMMARY


@app.post("/notes/{note_id}/summary")
def summarize(note_id: str, user: str = Depends(get_current_user)):
    note = notes_collection.find_one(
        {"id": note_id, "owner": user},
        {"_id": 0}
    )

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.get("summary"):
        return {"status": "success", "summary": note["summary"]}

    summary = generate_summary(note["content"])

    notes_collection.update_one(
        {"id": note_id, "owner": user},
        {"$set": {"summary": summary}}
    )

    return {"status": "success", "summary": summary}
