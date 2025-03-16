from pydantic.main import BaseModel


class UserReqst(BaseModel):
    username: str
    full_name: str
    email: str
    hashed_password: str
    disabled: bool = False
