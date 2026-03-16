from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from database import execute_query, get_connection
from datetime import datetime, timedelta
import psycopg2.extras
import bcrypt
import jwt
import re
import os


def execute_write(sql, params=None):
    """Execute INSERT/UPDATE/DELETE with autocommit (execute_query doesn't commit)."""
    conn = get_connection()
    conn.autocommit = True
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            try:
                rows = cur.fetchall()
                return [dict(row) for row in rows]
            except Exception:
                return []
    finally:
        conn.close()

router = APIRouter()
security = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hinova-monitor-fallback-change-me")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = TOKEN_EXPIRE_HOURS * 3600
    user: dict


def create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"}
        )


def require_role(*allowed_roles: str):
    def check_role(token_data: dict = Depends(verify_token)) -> dict:
        if token_data.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Perfil '{token_data.get('role')}' não tem permissão."
            )
        return token_data
    return check_role


require_admin = require_role("admin")
require_analyst = require_role("admin", "analyst")
require_viewer = require_role("admin", "analyst", "viewer")


@router.post("/auth/login", response_model=TokenResponse)
def login(body: LoginRequest):
    rows = execute_query(
        "SELECT id, username, password_hash, full_name, role "
        "FROM dw_monitor_users "
        "WHERE username = %s AND is_active = TRUE",
        (body.username,)
    )

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos."
        )

    user = rows[0]

    if not bcrypt.checkpw(body.password.encode(), user["password_hash"].encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos."
        )

    # Update last_login
    execute_write(
        "UPDATE dw_monitor_users SET last_login = NOW() WHERE id = %s RETURNING id",
        (user["id"],)
    )

    token = create_token(user["id"], user["username"], user["role"])

    return TokenResponse(
        access_token=token,
        user={
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    )


@router.get("/auth/me")
def get_me(token_data: dict = Depends(verify_token)):
    rows = execute_query(
        "SELECT id, username, full_name, role, last_login "
        "FROM dw_monitor_users WHERE username = %s",
        (token_data["username"],)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user = rows[0]
    return {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "last_login": user["last_login"].isoformat() if user["last_login"] else None
    }


@router.post("/auth/logout")
def logout(token_data: dict = Depends(verify_token)):
    return {"message": "Logout realizado com sucesso."}


# ── User Management Models ────────────────────────────────────

class CreateUserRequest(BaseModel):
    username: str
    password: str
    full_name: str = ""
    role: str = "viewer"


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


VALID_ROLES = ("admin", "analyst", "viewer")


# ── User Management Endpoints (admin only) ────────────────────

@router.get("/auth/users")
def list_users(token_data: dict = Depends(require_admin)):
    rows = execute_query("""
        SELECT id, username, full_name, role, is_active,
               created_at, last_login
        FROM dw_monitor_users
        ORDER BY created_at ASC
    """)
    return {
        "data": [
            {
                "id": r["id"],
                "username": r["username"],
                "full_name": r["full_name"] or "",
                "role": r["role"],
                "is_active": r["is_active"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "last_login": r["last_login"].isoformat() if r["last_login"] else None
            }
            for r in rows
        ],
        "updated_at": datetime.utcnow().isoformat()
    }


@router.post("/auth/users", status_code=201)
def create_user(body: CreateUserRequest, token_data: dict = Depends(require_admin)):
    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Role inválido. Use: admin, analyst ou viewer")

    if not re.match(r'^[a-zA-Z0-9._]{3,50}$', body.username):
        raise HTTPException(
            status_code=400,
            detail="Username inválido. Use 3-50 chars: letras, números, ponto ou underscore"
        )

    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 6 caracteres")

    exists = execute_query(
        "SELECT 1 FROM dw_monitor_users WHERE username = %s", (body.username,)
    )
    if exists:
        raise HTTPException(status_code=409, detail=f"Username '{body.username}' já existe")

    password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()

    result = execute_write("""
        INSERT INTO dw_monitor_users (username, password_hash, full_name, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, username, full_name, role, is_active, created_at
    """, (body.username, password_hash, body.full_name, body.role))

    return {"data": result[0], "message": f"Usuário '{body.username}' criado com sucesso"}


@router.put("/auth/users/{user_id}")
def update_user(user_id: int, body: UpdateUserRequest, token_data: dict = Depends(require_admin)):
    rows = execute_query(
        "SELECT id, username, role, is_active FROM dw_monitor_users WHERE id = %s",
        (user_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    target = rows[0]

    # Cannot deactivate yourself
    if body.is_active is False and target["username"] == token_data["username"]:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta")

    # Cannot demote the last active admin
    if body.role and body.role != "admin" and target["role"] == "admin":
        admin_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM dw_monitor_users WHERE role = 'admin' AND is_active = TRUE"
        )
        if admin_count[0]["cnt"] <= 1:
            raise HTTPException(
                status_code=400,
                detail="Não é possível rebaixar o único admin ativo do sistema"
            )

    # Cannot deactivate the last active admin
    if body.is_active is False and target["role"] == "admin":
        admin_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM dw_monitor_users WHERE role = 'admin' AND is_active = TRUE"
        )
        if admin_count[0]["cnt"] <= 1:
            raise HTTPException(
                status_code=400,
                detail="Não é possível desativar o único admin ativo do sistema"
            )

    if body.role and body.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail="Role inválido. Use: admin, analyst ou viewer")

    fields = []
    values = []

    if body.full_name is not None:
        fields.append("full_name = %s")
        values.append(body.full_name)
    if body.role is not None:
        fields.append("role = %s")
        values.append(body.role)
    if body.is_active is not None:
        fields.append("is_active = %s")
        values.append(body.is_active)
    if body.password:
        if len(body.password) < 6:
            raise HTTPException(status_code=400, detail="Senha deve ter no mínimo 6 caracteres")
        fields.append("password_hash = %s")
        values.append(bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode())

    if not fields:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    values.append(user_id)
    result = execute_write(
        f"UPDATE dw_monitor_users SET {', '.join(fields)} WHERE id = %s "
        "RETURNING id, username, full_name, role, is_active",
        tuple(values)
    )

    return {"data": result[0], "message": "Usuário atualizado com sucesso"}


@router.delete("/auth/users/{user_id}")
def deactivate_user(user_id: int, token_data: dict = Depends(require_admin)):
    rows = execute_query(
        "SELECT id, username, role FROM dw_monitor_users WHERE id = %s", (user_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    target = rows[0]

    if target["username"] == token_data["username"]:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta")

    if target["role"] == "admin":
        admin_count = execute_query(
            "SELECT COUNT(*) AS cnt FROM dw_monitor_users WHERE role = 'admin' AND is_active = TRUE"
        )
        if admin_count[0]["cnt"] <= 1:
            raise HTTPException(
                status_code=400,
                detail="Não é possível desativar o único admin ativo do sistema"
            )

    execute_write(
        "UPDATE dw_monitor_users SET is_active = FALSE WHERE id = %s RETURNING id",
        (user_id,)
    )

    return {"message": f"Usuário '{target['username']}' desativado com sucesso"}


@router.post("/auth/users/{user_id}/reactivate")
def reactivate_user(user_id: int, token_data: dict = Depends(require_admin)):
    rows = execute_query(
        "SELECT id, username FROM dw_monitor_users WHERE id = %s", (user_id,)
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    execute_write(
        "UPDATE dw_monitor_users SET is_active = TRUE WHERE id = %s RETURNING id",
        (user_id,)
    )
    return {"message": f"Usuário '{rows[0]['username']}' reativado com sucesso"}
