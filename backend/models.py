from pydantic.main import BaseModel


class UserReqst(BaseModel):
    username: str
    full_name: str
    email: str
    hashed_password: str
    disabled: bool = False


class AddToCart(BaseModel):
    user_id: int
    product_id: int
    quantity: int


class ProductCreateSchema(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category_ids: list[int] | None = None


class CategoryCreate(BaseModel):
    name: str
    description: str
