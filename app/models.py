# app/models.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import UserMixin

db = SQLAlchemy()

SCHEMA = "atllocal_db"


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


class MyUser(UserMixin, db.Model):
    __tablename__ = "my_user"
    __table_args__ = {"schema": SCHEMA}

    my_user_id     = db.Column(db.Integer, primary_key=True)
    first_name     = db.Column(db.String(255), nullable=False)
    last_name      = db.Column(db.String(255), nullable=False)
    email          = db.Column(db.String(300), nullable=False, unique=True)
    gender         = db.Column(db.String(20),  nullable=False)
    dob            = db.Column(db.Date,        nullable=False)
    zip_code       = db.Column(db.String(10),  nullable=False)
    city_state     = db.Column(db.String(300))
    image          = db.Column(db.String(300), nullable=False)

    # --- New auth fields ---
    password_hash  = db.Column(db.String(255), nullable=False)
    is_active      = db.Column(db.Boolean, default=True, nullable=False)
    is_admin       = db.Column(db.Boolean, default=False, nullable=False)
    is_member       = db.Column(db.Boolean, default=False, nullable=False)   
    last_login     = db.Column(db.DateTime(timezone=True))
    email_verified = db.Column(db.Boolean, default=False, nullable=False)

    created_at     = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at     = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ORM relationship
    posts = db.relationship("BlogPost", back_populates="author")

    # Flask-Login requires this property
    def get_id(self):
        return str(self.my_user_id)

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
    analytics = db.relationship("PostAnalytics", back_populates="post", uselist=False, cascade="all, delete-orphan")  

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
    

class NewsMain(db.Model):
    """
    Represents the current/past 'main story' windows for news posts.
    Only one active main story should exist at any given time (enforced in DB).
    """
    __tablename__ = "news_main"
    __table_args__ = {"schema": SCHEMA}

    # PK
    news_main_id = db.Column(db.Integer, primary_key=True)

    # FK to news_post (per your DDL) — ON DELETE CASCADE is in the database
    post_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{SCHEMA}.news_post.post_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Window (DATEs, not timestamps)
    start_date = db.Column(db.Date, nullable=False)
    end_date   = db.Column(db.Date, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Optional notes
    notes = db.Column(db.Text)

    # --- Relationships ---
    # Link to the NewsPost row (uselist=False because it's 1:1 by PK)
    news_post = db.relationship(
        "NewsPost",
        backref=db.backref("news_main_entries", cascade="all, delete-orphan", passive_deletes=True),
        uselist=False,
        lazy="joined",
    )

    @property
    def post(self):
        """
        Convenience: return the related BlogPost (via NewsPost → BlogPost).
        This lets API code use `nm.post` directly.
        """
        return self.news_post.post if self.news_post is not None else None

    def __repr__(self):
        return f"<NewsMain id={self.news_main_id} post_id={self.post_id} {self.start_date}→{self.end_date}>"

class PostAnalytics(db.Model):
    """
    1:1 analytics row per BlogPost.
    Mirrors DDL in atllocal_db.post_analytics (unique post_id, ON DELETE CASCADE).
    """
    __tablename__ = "post_analytics"
    __table_args__ = (
        db.UniqueConstraint("post_id", name="post_analytics_post_id_unique"),
        {"schema": SCHEMA},
    )

    post_analytics_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(
        db.Integer,
        db.ForeignKey(f"{SCHEMA}.blog_post.post_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    views    = db.Column(db.Integer, nullable=False, server_default="0")
    likes    = db.Column(db.Integer, nullable=False, server_default="0")
    comments = db.Column(db.Integer, nullable=False, server_default="0")
    shares   = db.Column(db.Integer, nullable=False, server_default="0")

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # ORM relationship back to BlogPost
    post = db.relationship("BlogPost", back_populates="analytics", lazy="joined")

    def __repr__(self):
        return f"<PostAnalytics id={self.post_analytics_id} post_id={self.post_id} views={self.views}>"


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

