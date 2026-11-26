from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class UserRegister(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6)
    full_name: str
    age: Optional[int] = 25
    gender: Optional[str] = "Other"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None

class PredictRequest(BaseModel):
    symptoms: List[str]
    user_id: Optional[str] = None

class FeedbackRequest(BaseModel):
    prediction_id: str
    rating: int = Field(..., ge=0, le=1) # 1 = useful, 0 = not useful
    comment: Optional[str] = ""

class RoleUpdate(BaseModel):
    user_id: str
    role: str # "USER" or "ADMIN"
    is_active: Optional[bool] = True
