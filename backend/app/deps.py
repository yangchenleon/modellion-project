from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .db import get_db
from .models import User
from .security import decode_token


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    import logging
    logger = logging.getLogger(__name__)
    
    if creds is None or not creds.credentials:
        logger.warning("认证失败: 未提供凭证")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未认证")
    
    logger.info(f"收到认证请求，token前10位: {creds.credentials[:10]}...")
    
    try:
        payload = decode_token(creds.credentials)
        logger.info(f"Token解码成功，用户: {payload.get('sub')}")
    except Exception as e:
        logger.error(f"Token解码失败: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")
    
    username = payload.get("sub")
    if not username:
        logger.warning("Token中无用户名")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效")
    
    user = db.query(User).filter(User.username == username).one_or_none()
    if user is None:
        logger.warning(f"用户不存在: {username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")
    
    logger.info(f"认证成功: {username}")
    return user


async def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足，仅管理员可执行")
    return user
