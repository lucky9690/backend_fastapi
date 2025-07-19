from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from camera import VideoCamera
from pydantic import BaseModel
from auth import (
    authenticate_user, create_access_token, get_current_user,
    hash_password, get_db
)
from models import User
from database import Base, engine
from starlette.responses import StreamingResponse
from utils import save_image
import cv2


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for safety
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
camera = VideoCamera()

@app.post("/register")
def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(
        username=form_data.username,
        hashed_password=hash_password(form_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User created successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/")
def root():
    return {"msg": "Wildlife Monitoring API"}

@app.get("/video_feed")
def video_feed(current_user: User = Depends(get_current_user)):
    def generate_frames():
        while True:
            frame = camera.get_frame()
            if frame:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/capture")
def capture_image(current_user: User = Depends(get_current_user)):
    ret, frame = camera.video.read()
    if not ret:
        return {"error": "Camera error"}
    path = save_image(frame)
    return {"message": "Image saved", "file": path}




