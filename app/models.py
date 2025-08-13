# app/models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

SCHEMA = "atllocal_db"

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Property {self.title}>'

class BlogCategory(db.Model):
    __tablename__ = "blog_category"
    __table_args__ = {"schema": SCHEMA}

    blog_cat_id = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(255), nullable=False, unique=True)
    slug        = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at  = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ORM relationship
    posts = db.relationship("BlogPost", back_populates="category")

    def __repr__(self):
        return f"<BlogCategory {self.slug}>"


class MyUser(db.Model):
    __tablename__ = "my_user"
    __table_args__ = {"schema": SCHEMA}

    my_user_id  = db.Column(db.Integer, primary_key=True)
    first_name  = db.Column(db.String(255), nullable=False)
    last_name   = db.Column(db.String(255), nullable=False)
    email       = db.Column(db.String(300), nullable=False)
    gender      = db.Column(db.String(20),  nullable=False)
    dob         = db.Column(db.Date,        nullable=False)
    zip_code    = db.Column(db.String(10),  nullable=False)
    city_state  = db.Column(db.String(300))
    image       = db.Column(db.String(300), nullable=False)
    created_at  = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at  = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ORM relationship
    posts = db.relationship("BlogPost", back_populates="author")

    def __repr__(self):
        return f"<MyUser {self.my_user_id} {self.email}>"


class BlogPost(db.Model):
    __tablename__ = "blog_post"
    __table_args__ = {"schema": SCHEMA}

    post_id        = db.Column(db.Integer, primary_key=True)
    title          = db.Column(db.String(255), nullable=False, unique=True)
    slug           = db.Column(db.String(255), nullable=False, unique=True)
    blog_cat_id    = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.blog_category.blog_cat_id"), nullable=False)
    author_id      = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.my_user.my_user_id"),       nullable=False)
    image          = db.Column(db.String(300), nullable=False)
    # Ensure your DB column has been renamed from content_uuid -> content_mongo_id
    content_mongo_id = db.Column(db.String(255))  # stores Mongo _id as a string (or another external key)
    created_at     = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at     = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ORM relationships
    category = db.relationship("BlogCategory", back_populates="posts")
    author   = db.relationship("MyUser",      back_populates="posts")
    news     = db.relationship("NewsPost",    back_populates="post", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BlogPost {self.slug}>"


class NewsPost(db.Model):
    """
    One-to-one extension of BlogPost (same primary key).
    Matches table `news_post (post_id PK/FK -> blog_post.post_id)`.
    """
    __tablename__ = "news_post"
    __table_args__ = {"schema": SCHEMA}

    post_id = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.blog_post.post_id"), primary_key=True)

    # Backref to the base BlogPost row
    post = db.relationship("BlogPost", back_populates="news")

    def __repr__(self):
        return f"<NewsPost post_id={self.post_id}>"