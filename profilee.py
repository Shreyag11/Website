from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import csv

app = FastAPI()

# Function to determine user type (alumni or current Ashokan)
def get_user_type(email):
    # You can implement your logic here to determine the user type based on the email domain
    # For demonstration purposes, let's assume if the email domain ends with "example.com", it's an alumni
    if email.endswith("example.com"):
        return "alumni"
    else:
        return "current"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return {"message": "Welcome to Ashoka Career Compass"}

@app.get("/profile", response_class=HTMLResponse)
async def read_profile():
    return {"message": "Fill out your profile"}

@app.post("/submit-profile")
async def submit_profile(request: Request, name: str = Form(...), email: str = Form(...),
                         course: str = Form(...), graduationYear: str = Form(...),
                         workExperience: str = Form(...), profile: str = Form(...),
                         domain: str = Form(...), role: str = Form(...)):
    
    # Determine user type
    user_type = get_user_type(email)

    # Write data to CSV file
    with open('profiles.csv', 'a', newline='') as csvfile:
        fieldnames = ['Username', 'Email', 'User Type', 'Course', 'Graduation Year', 'Work Experience', 'Profile', 'Domain', 'Role']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({'Username': name, 'Email': email, 'User Type': user_type, 'Course': course, 'Graduation Year': graduationYear,
                         'Work Experience': workExperience, 'Profile': profile, 'Domain': domain, 'Role': role})

    return RedirectResponse(url="/profile")
