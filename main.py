# 패키지 가져오기
import os
import cv2
import numpy as np
from insightface.app import FaceAnalysis
from fastapi import FastAPI, File, Request, UploadFile, Depends, Form
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
# DB 관련 패키지
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# import database
# import User


# 모델 가져와서 사용준비
face = FaceAnalysis(providers=['CPUExecutionProvider'])
face.prepare(ctx_id=0, det_size=(640, 640))

# fastapi 객체 생성하기
app = FastAPI()

# 템플릿 사용준비
templates = Jinja2Templates(directory="templates")

        
# 웹에 스트림 해준다.
@app.get("/")
async def Login(request: Request):    
    return templates.TemplateResponse("index.html", {"request": request})
        

@app.post("/loginface")
async def loginface(request: Request, imageFile: UploadFile = File(...)):
    # 클라이언트에서 전송한 이미지를 메모리 상에서 읽기
    contents1 = await request.form()
    contents1_bytes = await contents1["imageFile"].read()

    # 모든 이미지 파일과 비교
    image_dir_path = 'images'
    for filename in os.listdir(image_dir_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            reference_image_path = os.path.join(image_dir_path, filename)

            with open(reference_image_path, 'rb') as reference_image_file:
                reference_image_nparr = np.frombuffer(reference_image_file.read(), np.uint8)
            opencv_image2 = cv2.imdecode(reference_image_nparr, cv2.IMREAD_COLOR)

            # 클라이언트에서 전송한 이미지와 각 이미지를 비교
            nparr = np.frombuffer(contents1_bytes, np.uint8)
            opencv_image1 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # 변환한 파일 추론기에서 작업하기
            face1 = face.get(opencv_image1)
            face2 = face.get(opencv_image2)

            # 반환 해주기
            feat1 = np.array(face1[0].normed_embedding, dtype=np.float32)
            feat2 = np.array(face2[0].normed_embedding, dtype=np.float32)
            sims = np.dot(feat1, feat2)
            print(sims)

            if sims > 0.55:
                result = {"result": "입장하세요"}
                return JSONResponse(content=result)

    # 모든 이미지를 검사했는데 일치하는 얼굴이 없을 경우
    result = {"result": "등록되지 않은 사용자 입니다."}
    return JSONResponse(content=result)


# user를 등록 db 사용
# @app.post("/Upload")
# async def User_face(request: Request, name: str = Form(...),db: Session = Depends(database.get_db)):
#     # 사용자 이름 및 개인정보 (사번)
#     update_face = User.User(id=id)

#     db.add(update_face)
#     db.commit()

#     insert_face = await request.form()
#     insert_face_bytes = await insert_face["imageFile"].read()
#     image_dir_path = 'images'
#     image_file_path = os.path.join(image_dir_path, 'captured_image.jpg')

#     # 클라이언트에서 전송한 이미지 저장
#     with open(image_file_path, 'wb') as image_file:
#         image_file.write(insert_face_bytes)
