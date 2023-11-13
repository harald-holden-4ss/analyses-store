import os
from typing import Optional

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import exceptions, jwt

from app.models.user import User

B2C_DISCOVERY_KEYS_URL: str = os.environ.get("B2C_DISCOVERY_KEYS_URL", "")
if not B2C_DISCOVERY_KEYS_URL:
    raise KeyError("env var B2C_DISCOVERY_KEYS_URL not found")
ALLOWED_TOKEN_AUD: str = os.environ.get("ALLOWED_TOKEN_AUD", "")
if not ALLOWED_TOKEN_AUD:
    raise KeyError("env var ALLOWED_TOKEN_AUD not found")
ENVIRONMENT = os.environ.get("ENVIRONMENT", default="production")

# Get the keys from B2C URL
key = requests.get(B2C_DISCOVERY_KEYS_URL).json()

get_bearer_token = HTTPBearer(auto_error=False)


async def get_user(
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
) -> User:
    """
    Authenticate and retrieve user information from a JWT token.

    Parameters
    ----------
    authorization : Optional[HTTPAuthorizationCredentials], optional
        The authorization credentials, obtained from the HTTP Authorization header.

    Returns
    -------
    User
        The user object containing name, email, and organization ID.

    Raises
    ------
    HTTPException
        If the authentication header is empty or in the wrong format, or if the token is expired or invalid.
    """
    if ENVIRONMENT == "development":
        return User(
            name="John Doe",
            email="john@doe.com",
            organizationId="2c4ee562-6261-4018-a1b1-8837ab526944",
        )
    if not authorization:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Authentication header is empty or wrong format",
        )
    token = authorization.credentials.replace("Bearer", "").strip()
    try:
        algorithm = jwt.get_unverified_header(token).get("alg")
        user_info = jwt.decode(
            token=token, key=key, audience=ALLOWED_TOKEN_AUD, algorithms=algorithm
        )
        return User(
            name=user_info["name"],
            email=user_info["email"],
            organizationId=user_info["organizationId"],
        )
    except exceptions.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token has expired")

    except Exception as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token is invalid")


def check_acceptable_organization(user: User = Depends(get_user)) -> User:
    """
    Check if user with organization ID has access

    Parameters
    ----------
    user : User
        The user object to be checked

    Returns
    -------
    User
        The user object containing name, email, and organization ID.

    Raises
    ------
    HTTPException
        If the user organization is not authorized
    """
    if user.organizationId == "2c4ee562-6261-4018-a1b1-8837ab526944":
        return user
    else:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=f"Authorization refused for organization id {user.organizationId}",
        )


authorized_user = Depends(check_acceptable_organization)
