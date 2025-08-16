# app/schemas.py
from marshmallow import Schema, fields, validates, validates_schema, ValidationError, INCLUDE
import re

# --- Helpers (kept from earlier BlogCategory work) ---
def _slugify(text: str) -> str:
    return (
        (text or "").strip().lower()
        .replace("’", "'")
        .replace("&", "and")
        .replace("/", "-")
        .replace(" ", "-")
    )

# ======================================================
# BlogCategory Schemas
# ======================================================
class BlogCategoryCreateSchema(Schema):
    title = fields.String(required=True)
    slug = fields.String(required=True)
    description = fields.String(allow_none=True)

    @validates("title")
    def validate_title(self, value):
        if not value or not value.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def validate_slug(self, value):
        if not value or not value.strip():
            raise ValidationError("Slug cannot be empty.")
        if value != _slugify(value):
            raise ValidationError("Slug must be URL-safe (lowercase, hyphenated).")

class BlogCategoryUpdateSchema(Schema):
    title = fields.String(required=False)
    slug = fields.String(required=False)
    description = fields.String(required=False, allow_none=True)

    @validates("title")
    def validate_title(self, value):
        if value is not None and not value.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def validate_slug(self, value):
        if value is not None:
            if not value.strip():
                raise ValidationError("Slug cannot be empty.")
            if value != _slugify(value):
                raise ValidationError("Slug must be URL-safe (lowercase, hyphenated).")

class BlogCategoryOutSchema(Schema):
    blog_cat_id = fields.Integer()
    title       = fields.String()
    slug        = fields.String()
    description = fields.String(allow_none=True)
    created_at  = fields.DateTime(allow_none=True)
    updated_at  = fields.DateTime(allow_none=True)

blog_category_out = BlogCategoryOutSchema()
blog_category_list_out = BlogCategoryOutSchema(many=True)
blog_category_create = BlogCategoryCreateSchema()
blog_category_update = BlogCategoryUpdateSchema()

# ======================================================
# MyUser Schemas
# ======================================================
_US_ZIP_RE = re.compile(r"^\d{5}(?:-\d{4})?$")

class MyUserCreateSchema(Schema):
    first_name = fields.String(required=True)
    last_name  = fields.String(required=True)
    email      = fields.Email(required=True)
    gender     = fields.String(required=True)
    dob        = fields.Date(required=True)
    zip_code   = fields.String(required=True)
    city_state = fields.String(required=False, allow_none=True)
    image      = fields.String(required=True)

    @validates("first_name")
    def _v_first_name(self, v):
        if not v or not v.strip():
            raise ValidationError("First name cannot be empty.")
        if len(v) > 255:
            raise ValidationError("First name too long (max 255).")

    @validates("last_name")
    def _v_last_name(self, v):
        if not v or not v.strip():
            raise ValidationError("Last name cannot be empty.")
        if len(v) > 255:
            raise ValidationError("Last name too long (max 255).")

    @validates("gender")
    def _v_gender(self, v):
        if not v or not v.strip():
            raise ValidationError("Gender cannot be empty.")
        if len(v) > 20:
            raise ValidationError("Gender too long (max 20).")

    @validates("zip_code")
    def _v_zip(self, v):
        if not v or not v.strip():
            raise ValidationError("ZIP code cannot be empty.")
        if len(v) > 10:
            raise ValidationError("ZIP code too long (max 10).")
        if re.fullmatch(r"[0-9\-]+", v) and not _US_ZIP_RE.match(v):
            raise ValidationError("ZIP must be 12345 or 12345-6789.")

    @validates("image")
    def _v_image(self, v):
        if not v or not v.strip():
            raise ValidationError("Image path/URL cannot be empty.")
        if len(v) > 300:
            raise ValidationError("Image path too long (max 300).")

class MyUserUpdateSchema(Schema):
    first_name = fields.String(required=False)
    last_name  = fields.String(required=False)
    email      = fields.Email(required=False)
    gender     = fields.String(required=False)
    dob        = fields.Date(required=False)
    zip_code   = fields.String(required=False)
    city_state = fields.String(required=False, allow_none=True)
    image      = fields.String(required=False)

    @validates("first_name")
    def _v_first_name(self, v):
        if v is not None:
            if not v.strip():
                raise ValidationError("First name cannot be empty.")
            if len(v) > 255:
                raise ValidationError("First name too long (max 255).")

    @validates("last_name")
    def _v_last_name(self, v):
        if v is not None:
            if not v.strip():
                raise ValidationError("Last name cannot be empty.")
            if len(v) > 255:
                raise ValidationError("Last name too long (max 255).")

    @validates("gender")
    def _v_gender(self, v):
        if v is not None:
            if not v.strip():
                raise ValidationError("Gender cannot be empty.")
            if len(v) > 20:
                raise ValidationError("Gender too long (max 20).")

    @validates("zip_code")
    def _v_zip(self, v):
        if v is not None:
            if not v.strip():
                raise ValidationError("ZIP code cannot be empty.")
            if len(v) > 10:
                raise ValidationError("ZIP code too long (max 10).")
            if re.fullmatch(r"[0-9\-]+", v) and not _US_ZIP_RE.match(v):
                raise ValidationError("ZIP must be 12345 or 12345-6789.")

    @validates("image")
    def _v_image(self, v):
        if v is not None:
            if not v.strip():
                raise ValidationError("Image path/URL cannot be empty.")
            if len(v) > 300:
                raise ValidationError("Image path too long (max 300).")

class MyUserOutSchema(Schema):
    my_user_id = fields.Integer()
    first_name = fields.String()
    last_name  = fields.String()
    email      = fields.String()
    gender     = fields.String()
    dob        = fields.Date()
    zip_code   = fields.String()
    city_state = fields.String(allow_none=True)
    image      = fields.String()
    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)

my_user_out = MyUserOutSchema()
my_user_list_out = MyUserOutSchema(many=True)
my_user_create = MyUserCreateSchema()
my_user_update = MyUserUpdateSchema()

# ======================================================
# BlogPost Schemas
# ======================================================
class BlogPostOutSchema(Schema):
    post_id           = fields.Integer()
    title             = fields.String()
    slug              = fields.String()
    blog_cat_id       = fields.Integer()
    author_id         = fields.Integer()
    image             = fields.String()
    content_mongo_id  = fields.String(allow_none=True)
    created_at        = fields.DateTime(allow_none=True)
    updated_at        = fields.DateTime(allow_none=True)
    author_first_name = fields.Function(lambda o: getattr(o.author, "first_name", None))
    category_title    = fields.Function(lambda o: getattr(o.category, "title", None))

blog_post_out = BlogPostOutSchema()
blog_post_list_out = BlogPostOutSchema(many=True)

# ======================================================
# BlogPost Schemas (fixed validator signatures)
# ======================================================
class BlogPostCreateSchema(Schema):
    title             = fields.String(required=True)
    slug              = fields.String(required=True)
    blog_cat_id       = fields.Integer(required=True)
    author_id         = fields.Integer(required=True)
    image             = fields.String(required=True)
    content_mongo_id  = fields.String(allow_none=True)
    # ✅ allow the JSON you send from the form
    content           = fields.Dict(required=False)

    @validates("title")
    def _v_title(self, v, **kwargs):
        if not v or not v.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def _v_slug(self, v, **kwargs):
        if not v or not v.strip():
            raise ValidationError("Slug cannot be empty.")
        if v != _slugify(v):
            raise ValidationError("Slug must be URL-safe (lowercase, hyphenated).")

    @validates("image")
    def _v_image(self, v, **kwargs):
        if not v or not v.strip():
            raise ValidationError("Image path/URL cannot be empty.")
        if len(v) > 300:
            raise ValidationError("Image path too long (max 300).")


class BlogPostUpdateSchema(Schema):
    title             = fields.String()
    slug              = fields.String()
    blog_cat_id       = fields.Integer()
    author_id         = fields.Integer()
    image             = fields.String()
    content_mongo_id  = fields.String(allow_none=True)
    # ✅ allow partial updates that include content
    content           = fields.Dict(required=False)

    @validates("title")
    def _v_title(self, v, **kwargs):
        if v is not None and not v.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def _v_slug(self, v, **kwargs):
        if v is not None:
            if not v.strip():
                raise ValidationError("Slug cannot be empty.")
            if v != _slugify(v):
                raise ValidationError("Slug must be URL-safe (lowercase, hyphenated).")

    @validates("image")
    def _v_image(self, v, **kwargs):
        if v is not None:
            if not v.strip():
                raise ValidationError("Image path/URL cannot be empty.")
            if len(v) > 300:
                raise ValidationError("Image path too long (max 300).")
blog_post_create = BlogPostCreateSchema()
blog_post_update = BlogPostUpdateSchema()

# ======================================================
# NewsPost Schemas
# ======================================================
class NewsPostOutSchema(Schema):
    post_id          = fields.Integer()
    title            = fields.String()
    slug             = fields.String()
    blog_cat_id      = fields.Integer()
    author_id        = fields.Integer()
    image            = fields.String()
    content_mongo_id = fields.String(allow_none=True)
    created_at       = fields.DateTime(allow_none=True)
    updated_at       = fields.DateTime(allow_none=True)
    author_first_name = fields.Function(lambda o: getattr(o.author, "first_name", None))
    category_title    = fields.Function(lambda o: getattr(o.category, "title", None))

news_post_out = NewsPostOutSchema()
news_post_list_out = NewsPostOutSchema(many=True)

class NewsPostCreateSchema(Schema):
    post_id = fields.Integer(required=True)

class NewsPostUpdateSchema(Schema):
    post_id = fields.Integer()

news_post_create = NewsPostCreateSchema()
news_post_update = NewsPostUpdateSchema()

# ======================================================
# NewsMain Schemas
# ======================================================
class NewsMainOutSchema(Schema):
    news_main_id = fields.Integer()
    post_id      = fields.Integer()
    start_date   = fields.Date()
    end_date     = fields.Date()
    created_at   = fields.DateTime(allow_none=True)
    updated_at   = fields.DateTime(allow_none=True)
    notes        = fields.String(allow_none=True)
    author_first_name = fields.Function(
        lambda o: getattr(getattr(getattr(o, "post", None), "author", None), "first_name", None)
    )
    category_title = fields.Function(
        lambda o: getattr(getattr(getattr(o, "post", None), "category", None), "title", None)
    )

news_main_out = NewsMainOutSchema()
news_main_list_out = NewsMainOutSchema(many=True)

class NewsMainCreateSchema(Schema):
    post_id    = fields.Integer(required=True)
    start_date = fields.Date(required=True)
    end_date   = fields.Date(required=True)
    notes      = fields.String(allow_none=True)

    @validates_schema
    def _validate_dates(self, data, **kwargs):
        sd = data.get("start_date")
        ed = data.get("end_date")
        if sd is None or ed is None:
            raise ValidationError("Start date and end date are required.")
        if not (sd < ed):
            raise ValidationError("End date must be after start date.")

class NewsMainUpdateSchema(Schema):
    post_id    = fields.Integer()
    start_date = fields.Date()
    end_date   = fields.Date()
    notes      = fields.String(allow_none=True)

    @validates_schema
    def _validate_dates(self, data, **kwargs):
        sd = data.get("start_date")
        ed = data.get("end_date")
        if sd is not None and ed is not None and not (sd < ed):
            raise ValidationError("End date must be after start date.")

news_main_create = NewsMainCreateSchema()
news_main_update = NewsMainUpdateSchema()

# ======================================================
# PostAnalytics Schemas
# ======================================================
class PostAnalyticsOutSchema(Schema):
    post_analytics_id = fields.Integer()
    post_id           = fields.Integer()
    views             = fields.Integer()
    likes             = fields.Integer()
    comments          = fields.Integer()
    shares            = fields.Integer()
    created_at        = fields.DateTime(allow_none=True)
    updated_at        = fields.DateTime(allow_none=True)

post_analytics_out = PostAnalyticsOutSchema()
post_analytics_list_out = PostAnalyticsOutSchema(many=True)

class PostAnalyticsCreateSchema(Schema):
    post_id  = fields.Integer(required=True)
    views    = fields.Integer(load_default=0)
    likes    = fields.Integer(load_default=0)
    comments = fields.Integer(load_default=0)
    shares   = fields.Integer(load_default=0)

    @validates("views")
    def _v_views(self, v):
        if v is not None and v < 0:
            raise ValidationError("views cannot be negative.")

    @validates("likes")
    def _v_likes(self, v):
        if v is not None and v < 0:
            raise ValidationError("likes cannot be negative.")

    @validates("comments")
    def _v_comments(self, v):
        if v is not None and v < 0:
            raise ValidationError("comments cannot be negative.")

    @validates("shares")
    def _v_shares(self, v):
        if v is not None and v < 0:
            raise ValidationError("shares cannot be negative.")

class PostAnalyticsUpdateSchema(Schema):
    views    = fields.Integer()
    likes    = fields.Integer()
    comments = fields.Integer()
    shares   = fields.Integer()

    @validates("views")
    def _v_views(self, v):
        if v is not None and v < 0:
            raise ValidationError("views cannot be negative.")

    @validates("likes")
    def _v_likes(self, v):
        if v is not None and v < 0:
            raise ValidationError("likes cannot be negative.")

    @validates("comments")
    def _v_comments(self, v):
        if v is not None and v < 0:
            raise ValidationError("comments cannot be negative.")

    @validates("shares")
    def _v_shares(self, v):
        if v is not None and v < 0:
            raise ValidationError("shares cannot be negative.")

post_analytics_create = PostAnalyticsCreateSchema()
post_analytics_update = PostAnalyticsUpdateSchema()

# ------------------------------------------------------
# BlogPost + Analytics combined output
# ------------------------------------------------------
class BlogPostWithAnalyticsOutSchema(BlogPostOutSchema):
    views    = fields.Function(lambda o: getattr(getattr(o, "analytics", None), "views", 0))
    likes    = fields.Function(lambda o: getattr(getattr(o, "analytics", None), "likes", 0))
    comments = fields.Function(lambda o: getattr(getattr(o, "analytics", None), "comments", 0))
    shares   = fields.Function(lambda o: getattr(getattr(o, "analytics", None), "shares", 0))

blog_post_with_analytics_out = BlogPostWithAnalyticsOutSchema()
blog_post_with_analytics_list_out = BlogPostWithAnalyticsOutSchema(many=True)

# ======================================================
# Latest News Posts View Schema
# ======================================================
class LatestNewsPostsOutSchema(Schema):
    post_id     = fields.Integer()
    title       = fields.String()
    slug        = fields.String()
    image       = fields.String()
    blog_cat_id = fields.Integer()
    author_id   = fields.Integer()
    created_at  = fields.DateTime(allow_none=True)
    views       = fields.Integer()
    likes       = fields.Integer()
    comments    = fields.Integer()
    shares      = fields.Integer()

latest_news_posts_out = LatestNewsPostsOutSchema()
latest_news_posts_list_out = LatestNewsPostsOutSchema(many=True)
