from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio.session import AsyncSession

from models import AddToCart, CategoryCreate, ProductCreateSchema, UserReqst
from db import (
    add_to_cart,
    create_category,
    create_product,
    create_tables,
    create_test_user,
    get_all_products,
    get_async_db,
    get_user_by_username,
)

from config import settings

# Конфигурация JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

# User=Model(username="testuser",full_name="Test User",email="test@example.com",hashed_password="$2b$12$SErMU3rgP5PQ0Ji2m83osOaXi5QUQAlMKp0T86rxC0VA5zwY7ITay",disabled=False)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def create_refresh_token(username: str):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


async def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


async def get_user(db: AsyncSession, username: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    return user


async def authenticate_user(username: str, password: str, db: AsyncSession):
    user = await get_user(db, username)
    if user is None:
        return None
    elif await verify_password(password, user.hashed_password) != True:
        return None
    return user


async def get_current_user(db: AsyncSession, token: str):
    payload = await decode_token(token)

    if (
        not payload
        or (username := payload.get("sub")) is None
        or not isinstance(username, str)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await get_user(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


app = FastAPI()


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = await create_access_token({"sub": user.username})
    refresh_token = await create_refresh_token(user.username)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh")
async def refresh(refresh_token: str):
    payload = await decode_token(refresh_token)
    if payload is None or payload.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    username = payload.get("sub")
    new_access_token = create_access_token({"sub": username})
    return {"access_token": new_access_token, "token_type": "bearer"}


@app.get("/me/user")
async def read_users_me(
    db: AsyncSession = Depends(get_async_db), token: str = Depends(oauth2_scheme)
):
    return await get_current_user(db, token)


@app.get("/users/{username}")
async def read_user(username: str, db: AsyncSession = Depends(get_async_db)):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/migrate")
async def migrate():
    await create_tables()


@app.put("/create_user")
async def update_item(user: UserReqst, db: AsyncSession = Depends(get_async_db)):
    user.hashed_password = await get_password_hash(user.hashed_password)
    b = await create_test_user(db, user)
    return b


@app.post("/cart/add")
async def add_to_cart_endpoint(
    product_to_cart: AddToCart, db: AsyncSession = Depends(get_async_db)
):
    try:
        cart_item = await add_to_cart(
            db,
            product_to_cart.user_id,
            product_to_cart.product_id,
            product_to_cart.quantity,
        )
        return {"status": "success", "cart_item_id": cart_item.id}
    except ValueError as e:
        return {"status": "error", "message": str(e)}


@app.post("/products/")
async def create_new_product(
    product_data: ProductCreateSchema, db: AsyncSession = Depends(get_async_db)
):
    try:
        product = await create_product(
            db=db,
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock=product_data.stock,
            category_ids=product_data.category_ids,
        )
        return product
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/categories/")
async def create_new_category(
    category_data: CategoryCreate, db: AsyncSession = Depends(get_async_db)
):
    try:
        category = await create_category(
            db=db, name=category_data.name, description=category_data.description
        )
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/products/all")
async def get_products_sequence(db: AsyncSession = Depends(get_async_db)):
    all_products = await get_all_products(db)
    return all_products


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
