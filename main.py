from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import shutil

app = FastAPI()

# Mount static and images folders
app.mount("/static", StaticFiles(directory="static"), name="static")
if not os.path.exists("static/images"):
    os.makedirs("static/images")

templates = Jinja2Templates(directory="templates")

# Homepage
@app.get("/", response_class=HTMLResponse)
def read_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Browse page - show all items
@app.get("/browse", response_class=HTMLResponse)
def read_browse(request: Request):
    file_path = "items.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            items = json.load(f)
    else:
        items = []
    return templates.TemplateResponse("browse.html", {"request": request, "items": items})

# GET signup page
@app.get("/signup", response_class=HTMLResponse)
def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# POST signup form submission
@app.post("/signup")
async def post_signup(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    phone: str = Form(...),
    payment: str = Form(...),
    account_type: str = Form(...)
):
    user_data = {
        "name": name,
        "email": email,
        "address": address,
        "phone": phone,
        "payment": payment,
        "account_type": account_type
    }

    file_path = "users.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            users = json.load(f)
    else:
        users = []

    users.append(user_data)

    with open(file_path, "w") as f:
        json.dump(users, f, indent=4)

    # Redirect based on account type, passing email for personal sellers
    if account_type == "Personal Seller":
        return RedirectResponse(url=f"/personaloption?email={email}", status_code=303)
    elif account_type == "Enterprise Seller":
        return RedirectResponse(url="/business-membership", status_code=303)
    else:
        return RedirectResponse(url="/", status_code=303)

# GET personal option page
@app.get("/personaloption", response_class=HTMLResponse)
def get_personaloption(request: Request, email: str = ""):
    return templates.TemplateResponse("personaloption.html", {"request": request, "email": email})

# POST personal option form submission
@app.post("/personaloption")
async def post_personaloption(
    request: Request,
    email: str = Form(...),
    duration: str = Form(...),
    sale_area: str = Form(...),
    miles: str = Form(None),
    shipping: str = Form(...)
):
    # Load users
    file_path = "users.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            users = json.load(f)
    else:
        users = []

    # Find and update the user by email
    for user in users:
        if user["email"] == email:
            user["duration"] = duration
            user["sale_area"] = sale_area
            user["miles"] = miles
            user["shipping"] = shipping

    with open(file_path, "w") as f:
        json.dump(users, f, indent=4)

    # Redirect to add items page, passing email
    return RedirectResponse(url=f"/additems?email={email}", status_code=303)

# GET add items page
@app.get("/additems", response_class=HTMLResponse)
def get_additems(request: Request, email: str = ""):
    return templates.TemplateResponse("additems.html", {"request": request, "email": email})

# POST add items form submission
@app.post("/additems")
async def post_additems(
    request: Request,
    email: str = Form(...),
    item_name: str = Form(...),
    description: str = Form(...),
    price: str = Form(...),
    image: UploadFile = File(...)
):
    # Save image to static/images
    image_filename = image.filename
    image_path = os.path.join("static/images", image_filename)
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Save item data
    item_data = {
        "email": email,
        "item_name": item_name,
        "description": description,
        "price": price,
        "image_filename": image_filename
    }

    file_path = "items.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            items = json.load(f)
    else:
        items = []

    items.append(item_data)

    with open(file_path, "w") as f:
        json.dump(items, f, indent=4)

    # Redirect to browse page after adding item
    return RedirectResponse(url="/browse", status_code=303)