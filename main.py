from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse



app = FastAPI()
client = MongoClient('mongodb://localhost:27017/')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

# Define the route to serve the home page
@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("website.html", {"request": request})

@app.post('/signup')
def signup(user: User):
    db = client['user_authentication']
    users_collection = db['users']

    hashed_password = pwd_context.hash(user.password)

    if users_collection.find_one({'email': user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = {'name': user.name, 'email': user.email, 'hashed_password': hashed_password, 'status': user.status}
    users_collection.insert_one(user_data)

    return {'message': 'User signed up successfully!'}

@app.post('/login')
def login(email: str, password: str):
    db = client['user_authentication']
    users_collection = db['users']
    
    user_data = users_collection.find_one({'email': email})
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not pwd_context.verify(password, user_data['hashed_password']):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return {'message': 'Login successful'}
