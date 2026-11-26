import sys
import os
import base64
import hmac
import hashlib
from datetime import datetime, timedelta
import uuid
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer

from database.db import get_db_connection, get_password_hash, verify_password
from backend.schemas.schemas import UserRegister, UserLogin, TokenResponse, ProfileUpdate

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

SECRET_KEY = "SUPER_SECRET_AI_HEALTH_KEY_FOR_JWT_TOKEN"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def create_access_token(data: dict, expires_delta: timedelta = None):
    try:
        from jose import jwt
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    except Exception:
        # Fallback signed token encoder
        header = base64.b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode()
        payload_data = data.copy()
        expire_ts = int((datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))).timestamp())
        payload_data["exp"] = expire_ts
        payload = base64.b64encode(json.dumps(payload_data).encode()).decode()
        sig = hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).hexdigest()
        return f"{header}.{payload}.{sig}"

def decode_access_token(token: str):
    try:
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, sig = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        try:
            payload_data = json.loads(base64.b64decode(payload.encode()).decode())
            if payload_data.get("exp", 0) < int(datetime.utcnow().timestamp()):
                return None
            return payload_data
        except Exception:
            return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        # Return default guest/demo user for development ease
        return {
            "id": "guest_user",
            "email": "user@health.ai",
            "role": "USER",
            "full_name": "Demo Health User",
            "age": 28,
            "gender": "Female",
            "is_active": 1
        }

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.email, u.role, u.is_active, p.full_name, p.age, p.gender 
        FROM users u 
        LEFT JOIN profiles p ON u.id = p.user_id 
        WHERE u.id = ?
    """, (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        raise credentials_exception
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Account is deactivated.")

    return dict(user)

@router.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email.lower(),))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email is already registered.")

    user_id = str(uuid.uuid4())
    hashed_pwd = get_password_hash(user_data.password)

    cursor.execute(
        "INSERT INTO users (id, email, hashed_password, role, is_active) VALUES (?, ?, ?, ?, ?)",
        (user_id, user_data.email.lower(), hashed_pwd, "USER", 1)
    )

    profile_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO profiles (id, user_id, full_name, age, gender) VALUES (?, ?, ?, ?, ?)",
        (profile_id, user_id, user_data.full_name, user_data.age, user_data.gender)
    )

    conn.commit()
    conn.close()

    user_info = {
        "id": user_id,
        "email": user_data.email.lower(),
        "role": "USER",
        "full_name": user_data.full_name,
        "age": user_data.age,
        "gender": user_data.gender
    }

    token = create_access_token(data={"sub": user_id, "role": "USER"})
    return {"access_token": token, "token_type": "bearer", "user": user_info}

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.id, u.email, u.hashed_password, u.role, u.is_active, p.full_name, p.age, p.gender 
        FROM users u 
        LEFT JOIN profiles p ON u.id = p.user_id 
        WHERE u.email = ?
    """, (login_data.email.lower(),))
    user = cursor.fetchone()
    conn.close()

    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password credentials.")

    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Account has been deactivated. Please contact admin.")

    user_info = {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user["full_name"],
        "age": user["age"],
        "gender": user["gender"]
    }

    token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer", "user": user_info}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.put("/profile")
def update_profile(profile_data: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    full_name = profile_data.full_name or current_user["full_name"]
    age = profile_data.age if profile_data.age is not None else current_user["age"]
    gender = profile_data.gender or current_user["gender"]

    cursor.execute(
        "UPDATE profiles SET full_name = ?, age = ?, gender = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
        (full_name, age, gender, current_user["id"])
    )
    conn.commit()
    conn.close()

    return {"status": "success", "message": "Profile updated successfully.", "full_name": full_name, "age": age, "gender": gender}
