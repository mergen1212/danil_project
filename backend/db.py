from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    select,
    func,
    Table,
    Integer,
)
from sqlalchemy.orm import Mapped, relationship, mapped_column, selectinload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from models import CommentSchema, UserReqst
from typing import Sequence
from config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str] = mapped_column(default="")
    email: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    disabled: Mapped[bool] = mapped_column(default=False)

    # Отношения
    cart: Mapped[list["Cart"]] = relationship(back_populates="user")
    purchases: Mapped[list["Purchased"]] = relationship(back_populates="user")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str] = mapped_column()
    price: Mapped[float] = mapped_column()
    stock: Mapped[int] = mapped_column(default=0)

    # Отношения
    categories: Mapped[list["Category"]] = relationship(
        secondary=product_category, back_populates="products"
    )
    in_carts: Mapped[list["Cart"]] = relationship(back_populates="product")
    purchased: Mapped[list["Purchased"]] = relationship(back_populates="product")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column()
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    # Parent-child relationship
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id"), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="comments")
    product: Mapped["Product"] = relationship(back_populates="comments")
    replies: Mapped[list["Comment"]] = relationship(
        back_populates="parent", cascade="all, delete", passive_deletes=True
    )
    parent: Mapped["Comment"] = relationship(back_populates="replies", remote_side=[id])


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str] = mapped_column()

    # Связь с товарами (многие-ко-многим)
    products: Mapped[list["Product"]] = relationship(
        secondary=product_category, back_populates="categories"
    )


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(default=1)

    # Уникальная комбинация пользователя и товара в корзине
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="_user_product_uc"),
    )

    # Отношения
    user: Mapped["User"] = relationship(back_populates="cart")
    product: Mapped["Product"] = relationship(back_populates="in_carts")


class Purchased(Base):
    __tablename__ = "purchased"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column()
    purchase_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Отношения
    user: Mapped["User"] = relationship(back_populates="purchases")
    product: Mapped["Product"] = relationship(back_populates="purchased")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def add_to_cart(
    db: AsyncSession, user_id: int, product_id: int, quantity: int = 1
) -> Cart:
    user = await db.execute(select(User).filter(User.id == user_id))
    user = user.scalars().first()

    product = await db.execute(select(Product).filter(Product.id == product_id))
    product = product.scalars().first()

    if not user or not product:
        raise ValueError("Пользователь или товар не найдены")

    # Проверяем наличие товара в корзине
    cart_item = await db.execute(
        select(Cart)
        .filter(Cart.user_id == user_id)
        .filter(Cart.product_id == product_id)
    )
    cart_item = cart_item.scalars().first()

    if cart_item:
        # Обновляем количество
        cart_item.quantity += quantity
    else:
        # Создаем новую запись
        cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.add(cart_item)

    try:
        await db.commit()
        await db.refresh(cart_item)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Ошибка при добавлении в корзину")
    return cart_item


async def create_test_user(db: AsyncSession, user: UserReqst):
    test_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        hashed_password=user.hashed_password,
        disabled=user.disabled,
    )
    db.add(test_user)
    try:
        await db.commit()
        await db.refresh(test_user)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Ошибка при создании пользователя")
    return test_user


async def create_product(
    db: AsyncSession,
    name: str,
    description: str,
    price: float,
    stock: int = 0,
    category_ids: list[int] | None = None,
) -> Product:
    """
    Создает новый продукт и связывает его с категориями
    :param db: Асинхронная сессия
    :param name: Название продукта (уникальное)
    :param description: Описание
    :param price: Цена
    :param stock: Остаток на складе
    :param category_ids: Список ID категорий для связи
    :return: Созданный продукт
    """

    # Проверка валидности данных
    if price <= 0:
        raise ValueError("Цена должна быть положительным числом")
    if stock < 0:
        raise ValueError("Остаток не может быть отрицательным")

    # Создаем новый продукт
    new_product = Product(name=name, description=description, price=price, stock=stock)

    try:
        # Добавляем продукт в сессию
        db.add(new_product)

        # Получаем категории, если указаны
        if category_ids:
            categories = await db.execute(
                select(Category).filter(Category.id.in_(category_ids))
            )
            categories = categories.scalars().all()

            # Связываем категории с продуктом
            new_product.categories.extend(categories)

        # Фиксируем изменения
        await db.commit()
        await db.refresh(new_product)

    except IntegrityError as e:
        await db.rollback()
        if "UNIQUE constraint failed: products.name" in str(e):
            raise ValueError(f"Продукт с названием '{name}' уже существует")
        raise ValueError(f"Продукт {name} создать не удалось")
    return new_product


async def create_category(
    db: AsyncSession, name: str, description: str | None = None
) -> Category:
    """
    Создает новую категорию
    :param db: Асинхронная сессия
    :param name: Название категории (уникальное)
    :param description: Описание категории (опционально)
    :return: Созданная категория
    """
    # Проверяем существование категории с таким именем
    existing_category = await db.execute(select(Category).filter(Category.name == name))
    if existing_category.scalars().first():
        raise ValueError(f"Категория '{name}' уже существует")

    # Создаем новую категорию
    new_category = Category(name=name, description=description)

    try:
        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Ошибка при создании категории")

    return new_category


async def get_all_products(db: AsyncSession) -> Sequence[Product]:
    """
    Получает все продукты из базы данных
    :param db: Асинхронная сессия SQLAlchemy
    :return: Список продуктов
    """
    query = select(Product)
    result = await db.execute(query)
    return result.scalars().all()


async def create_reply_comment_or_comment(db: AsyncSession, CommentDTO: CommentSchema):
    if CommentDTO.parent_id is None:
        new_comment = Comment(
            text=CommentDTO.text,
            user_id=CommentDTO.user_id,
            product_id=CommentDTO.product_id,
        )
    else:
        new_comment = Comment(
            text=CommentDTO.text,
            user_id=CommentDTO.user_id,
            product_id=CommentDTO.product_id,
            parent_id=CommentDTO.parent_id,
        )
    db.add(new_comment)
    try:
        await db.commit()
        await db.refresh(new_comment)
        return new_comment
    except IntegrityError:
        await db.rollback()
        raise ValueError("Ошибка при создании коментария")


async def add_categories_to_product(
    db: AsyncSession, product_id: int, category_ids: list[int]
) -> Product:
    # Получаем продукт с предзагруженными категориями
    product = await db.get(
        Product, product_id, options=[selectinload(Product.categories)]
    )
    if not product:
        raise ValueError(f"Product with ID {product_id} not found")

    # Получаем запрашиваемые категории
    stmt = select(Category).where(Category.id.in_(category_ids))
    result = await db.execute(stmt)
    categories = result.scalars().all()

    # Фильтруем новые категории
    existing_category_ids = {c.id for c in product.categories}
    new_categories = [c for c in categories if c.id not in existing_category_ids]

    # Добавляем связи
    if new_categories:
        product.categories.extend(new_categories)
        try:
            await db.commit()
            await db.refresh(product, ["categories"])
        except Exception as e:
            await db.rollback()
            raise RuntimeError(f"Error adding categories: {str(e)}")

    return product
