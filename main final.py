from fastapi import FastAPI, HTTPException, Query, Request, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()
client = MongoClient('mongodb://localhost:27017/')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="secret-key")
# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")




# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000/templates/website.html"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

class User(BaseModel):
    name: str
    email: str
    password: str
    status: str
    role: str = None
    expertise: list = []


class Assignment(BaseModel):
    mentor: str
    mentee: str
    skill: str


def get_current_user(request: Request):
    user_email = request.session.get("user_email")
    if not user_email:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_email

# Define the route to serve the home page
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("website.html", {"request": request})

# Define the route to serve the dashboard page
@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request, current_user: str = Depends(get_current_user)):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# Define the route to serve the connect page
@app.get("/connect", response_class=HTMLResponse)
async def read_connect(request: Request, current_user: str = Depends(get_current_user)):
    return templates.TemplateResponse("connect.html", {"request": request})

@app.post("/find_connections")
async def find_suitable_candidates(request: Request, current_user: str = Depends(get_current_user)):
    data = await request.json()
    role = data["role"]

    db = client['user_authentication']
    users_collection = db['users']
    assignments_collection = db['assignments']

    current_user_data = users_collection.find_one({"email": current_user})
    expertise = current_user_data["expertise"]
    blacklist_emails = []
    if role == "mentor":
        # Find mentors who are not already assigned as mentees to the current user
        assigned_mentees = assignments_collection.distinct("mentee", {"mentor": current_user})
        blacklist_emails = assigned_mentees + [current_user]
        query = {"expertise": {"$in": expertise}}
    else:
        assigned_mentors = assignments_collection.distinct("mentor", {"mentee": current_user})
        blacklist_emails = assigned_mentors + [current_user]
        query = {"expertise": {"$in": expertise}}

    assigned_candidates = assignments_collection.distinct(role, {"$or": [{"mentor": current_user}, {"mentee": current_user}]})
    query["email"] = {"$nin": assigned_candidates + blacklist_emails}

    candidates = list(users_collection.find(query))

    if candidates:
        candidate = candidates[0]
        common_skill = next(skill for skill in expertise if skill in candidate["expertise"])

        if role == "mentee":
            assignment = Assignment(mentor=current_user, mentee=candidate["email"], skill=common_skill)
        else:
            assignment = Assignment(mentor=candidate["email"], mentee=current_user, skill=common_skill)

        assignments_collection.insert_one(assignment.dict())

        return {"message": "Assignment successful", "assignment": {
            "role": role,
            "candidate": candidate["name"],
            "skill": common_skill
        }}
    else:
        raise HTTPException(status_code=404, detail="No suitable candidates found")

@app.post("/signout")
async def signout(request: Request):
    request.session.clear()
    return JSONResponse(content={'message': 'Signed out successfully'})

@app.post('/signup')
def signup(request: Request, user: User):
    db = client['user_authentication']
    users_collection = db['users']

    hashed_password = pwd_context.hash(user.password)

    if users_collection.find_one({'email': user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = {'name': user.name, 'email': user.email, 'hashed_password': hashed_password, 'status': user.status,        'expertise': user.expertise, 'role': user.role}
    users_collection.insert_one(user_data)
    request.session["user_email"] = user.email

    return JSONResponse(content={'message': 'User signed up successfully!'})

@app.post('/login')
def login(request: Request, email: str = Query(...), password: str = Query(...)):
    db = client['user_authentication']
    users_collection = db['users']
    
    user_data = users_collection.find_one({'email': email})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(password, user_data['hashed_password']):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Store the user's email in the session
    request.session["user_email"] = email
    
    return JSONResponse(content={'message': 'Login successful'})

@app.get("/assignments")
async def get_assignments(current_user: str = Depends(get_current_user)):
    db = client['user_authentication']
    assignments_collection = db['assignments']
    users_collection = db['users']

    mentee_assignments = list(assignments_collection.find({"mentor": current_user}))
    mentor_assignments = list(assignments_collection.find({"mentee": current_user}))

    mentors = []
    mentees = []

    for assignment in mentee_assignments:
        mentee = users_collection.find_one({"email": assignment["mentee"]})
        mentees.append({"name": mentee["name"], "skill": assignment["skill"]})
    for assignment in mentor_assignments:
        mentor = users_collection.find_one({"email": assignment["mentor"]})
        mentors.append({"name": mentor["name"], "skill": assignment["skill"]})

    print(f"For user {current_user}, mentors: {mentors}, mentees: {mentees}")
    return {"mentors": mentors, "mentees": mentees}
