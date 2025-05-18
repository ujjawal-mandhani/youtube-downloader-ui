from pydantic import BaseModel, Field
from typing import Optional, Dict
import re

class BaseSignupSchema(BaseModel):
    username: str = Field(..., pattern=r"^[a-zA-Z0-9\s]+$")
    password: str = Field(..., pattern=r"^[A-Za-z\d@$!%*?&]{8,}$")
    customerid: str = Field(None, pattern=r"^[a-zA-Z0-9]+$")
    
class BaseLoginSchema(BaseModel):
    username: str = Field(..., pattern=r"^[a-zA-Z0-9\s]+$")
    password: str = Field(..., pattern=r"^[A-Za-z\d@$!%*?&]{8,}$")

class FetchVideoDetailsSchema(BaseModel):
    video_url: str = Field(...,pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$")
    jwt_token: str = Field(..., pattern=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$")
    
class DownloadVideoSchema(BaseModel):
    video_url: str = Field(...,pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$")
    jwt_token: str = Field(..., pattern=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$")

class FormatDetails(BaseModel):
    ext: str = Field(..., pattern=r"^.*$")
    resolution: str = Field(..., pattern=r"^.*$")

class VideoDetailsResponse(BaseModel):
    audio_video_formats: Dict[str, FormatDetails]
    title: str = Field(..., pattern=r"^.*$")
    jwt_token: str = Field(..., pattern=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$")
    video_url: str = Field(...,pattern=r"^(https?|ftp)://[^\s/$.?#].[^\s]*$")
    
class FetchUserActivitySchema(BaseModel):
    jwt_token: str = Field(..., pattern=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$")
    limit: str = Field(...,pattern=r"^\d+$")
    skip: str = Field(...,pattern=r"^\d+$")
    
class DeleteUserActivitySchema(BaseModel):
    jwt_token: str = Field(..., pattern=r"^[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+$")
    doc_id: str = Field(...,pattern=r"^[a-fA-F0-9]{24}$")