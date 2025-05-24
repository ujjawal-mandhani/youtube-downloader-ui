import uuid
import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from Schemas.Schemas import BaseSignupSchema, BaseLoginSchema, FetchVideoDetailsSchema, VideoDetailsResponse, FetchUserActivitySchema, DeleteUserActivitySchema
from Exception_handler.exceptions import validation_exception_handler
from utility.utils import list_video_details, update_headers, get_headers, get_date_time, hash_password_func, verify_password, generateJWTToken, build_response, verifyJWTToken, download_video_yt_dlp
from utility.custom_logger import logger
from models.mongodb_connection import insert_document, find_document, delete_document
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from bson import ObjectId


app = FastAPI()
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:9041"] for more secure setup
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
version = "/v1"
@app.post(f'{version}/signup')
async def signup(request: Request, signup_data: BaseSignupSchema, response: Response):
    cookies = request.cookies
    headers = request.headers
    response = update_headers(response)
    signup_dict = signup_data.dict()
    signup_dict["unique_identifier"] = str(uuid.uuid4())
    signup_dict["created_at"] = get_date_time()
    signup_dict["updated_timestamp"] = get_date_time()
    signup_dict["password"] = hash_password_func(signup_dict["password"])
    logger.info(signup_dict["password"])
    if signup_dict["customerid"] in [None, '']:
        signup_dict["customerid"] = str(uuid.uuid4()).replace('-', '')
    status_code, message, inserted_id = insert_document("login_signup_collection", signup_dict, parameters_to_check = [
        "username"
    ], db_name= "userbase_db")
    jwt_token = None
    if status_code == 200:
        jwt_token = generateJWTToken(signup_dict["customerid"])
    try:
        if jwt_token:
            resp = {
                "message": message,
                "token": jwt_token
            }
        else:
            resp = {
                "message": message
            }
        return build_response(resp, status_code)
    except Exception as E:
        print(E)
        return build_response({
                "errors": "Internal Server Error"
            }, 500)

@app.post(f'{version}/loginup')
async def loginup(request: Request, login_data: BaseLoginSchema, response: Response):
    cookies = request.cookies
    headers = request.headers
    response = update_headers(response)
    login_data = login_data.dict()
    status_code, document = find_document("login_signup_collection", query={
        "username": login_data["username"]
    }, db_name= "userbase_db")
    if status_code == 400:
        return build_response({
            "message": document    
        },status_code)
    print("::::::::::::login_data password", login_data["password"])
    if not verify_password(password=login_data["password"], hashed_password=document["password"]):
        status_code = 400
        message = {
            "message": "Password is not correct"
        }
        return build_response(message, status_code)
    jwt_token = generateJWTToken(document["customerid"])
    message = {
        "message": "login successfully",
        "token": jwt_token
    }
    try:
        return build_response(message, status_code)
    except Exception as E:
        print(E)
        message = {
            "errors": "Internal Server Error"
        }
        return build_response(message, 500)

@app.post(f'{version}/fetch_video_details')
async def fetch_video_details(request: Request, fetch_video_details_req: FetchVideoDetailsSchema, response: Response):
    response = update_headers(response)
    fetch_video_details_req = fetch_video_details_req.dict()
    print(fetch_video_details_req)
    # message = fetch_video_details_req
    # status_code= 200
    status_code, message = verifyJWTToken(fetch_video_details_req["jwt_token"])
    print(message, status_code)
    if status_code != 200:
        return build_response({
            "message": message
        }, status_code)
    status_code, video_details = list_video_details(fetch_video_details_req["video_url"])
    if status_code != 200:
        return build_response({
            "message": "Unable to find details Please check video URL"
        }, status_code)
    try:
        return build_response({
            "message": video_details
        }, status_code)
    except Exception as E:
        print(E)
        message = {
            "errors": "Internal Server Error"
        }
        return build_response(message, 500)

@app.post(f'{version}/download_video')
async def download_video(request: Request, download_video_request: VideoDetailsResponse, response: Response):
    print(download_video_request.dict())
    response = update_headers(response)
    download_video_request_payload = download_video_request.dict()
    status_code, message = verifyJWTToken(download_video_request_payload["jwt_token"])
    print(message, status_code)
    if status_code != 200:
        return build_response({
            "message": message
        }, status_code)
    cust_id = message
    status_code, local_video_url = download_video_yt_dlp(array_format_code = download_video_request_payload, customerid=cust_id, sub_title_format=download_video_request_payload.get("sub"), output_path='/home/videos/')
    if status_code != 200:
        return build_response({
            "message": local_video_url
        }, status_code)
    print("::::::::::::::::", Path(local_video_url["video_path"]).name)
    mongo_db_data = download_video_request_payload.copy()
    mongo_db_data.pop('jwt_token')
    try:
        mongo_data = {
            "customer_id": cust_id,
            "audit_timestamp": get_date_time(),
            "video_details": mongo_db_data,
        }
        insert_document("user_audit", mongo_data, [], db_name="userbase_db")
        response = update_headers(FileResponse(
            path=local_video_url["video_path"],
            media_type="application/octet-stream",  # Generic binary data
            filename=Path(local_video_url["video_path"]).name,  # Downloaded filename
        ))
        response.headers["Content-Disposition"] = f'attachment; filename="{Path(local_video_url["video_path"]).name.encode('latin-1', errors='ignore')}"'
        response.headers["Content-Type"] = "video/mp4"
        return response
    except Exception as E:
        print(E)
        message = {
            "errors": "Internal Server Error"
        }
        return build_response(message, 500)
    

@app.post(f'{version}/fetch_user_history')
async def fetch_user_history_paginated(request: Request, fetch_user_history_request: FetchUserActivitySchema, response: Response):
    print(fetch_user_history_request.dict())
    response = update_headers(response)
    fetch_user_history_request = fetch_user_history_request.dict()
    status_code, message = verifyJWTToken(fetch_user_history_request["jwt_token"])
    print(message, status_code)
    if status_code != 200:
        return build_response({
            "message": message
        }, status_code)
    cust_id = message
    status_code, response_from_mongo_db = find_document("user_audit", query= {
        "customer_id": cust_id
    }, db_name="userbase_db", skip=int(fetch_user_history_request["skip"]), limit=int(fetch_user_history_request["limit"]))
    try:
        return build_response({
                "message": response_from_mongo_db
            }, status_code)
    except Exception as E:
        print(E)
        message = {
            "errors": "Internal Server Error"
        }
        return build_response(message, 500)
    
@app.post(f'{version}/delete_user_history')
async def delete_user_history_func(request: Request, delete_user_history_request: DeleteUserActivitySchema, response: Response):
    print(delete_user_history_request.dict())
    response = update_headers(response)
    delete_user_history_request = delete_user_history_request.dict()
    status_code, message = verifyJWTToken(delete_user_history_request["jwt_token"])
    print(message, status_code)
    if status_code != 200:
        return build_response({
            "message": message
        }, status_code)
    cust_id = message
    status_code, response_from_mongo_db = delete_document("user_audit", query= {
        "_id": ObjectId(f"{delete_user_history_request["doc_id"]}"),
        "customer_id": cust_id
    }, db_name="userbase_db")
    print(":::::::::::::response from mongo db", response_from_mongo_db)
    try:
        return build_response({
                "message": response_from_mongo_db
            }, status_code)
    except Exception as E:
        print(E)
        message = {
            "errors": "Internal Server Error"
        }
        return build_response(message, 500)