from pydantic.main import BaseModel


class CategoryUpdateRequest(BaseModel):
    category_ids: list[int]


class UserReqst(BaseModel):
    username: str
    full_name: str | None = None
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


class UserLogSchema(BaseModel):
    name: str
    password: str


class CommentSchema(BaseModel):
    text: str
    user_id: int  # ID менеджера магазина
    product_id: int
    parent_id: int | None = None
