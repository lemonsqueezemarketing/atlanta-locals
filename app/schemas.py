# app/schemas.py
from marshmallow import Schema, fields, validates, ValidationError
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
# BlogCategory Schemas (as finalized earlier)
# ======================================================
class BlogCategoryCreateSchema(Schema):
    # For POST and PUT: both required to match DB constraints
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
    # For PATCH: all optional, but if present must be valid
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
# Model (for reference):
#   my_user_id PK
#   first_name (NOT NULL), last_name (NOT NULL), email (NOT NULL), gender (NOT NULL),
#   dob (NOT NULL, Date), zip_code (NOT NULL), city_state (NULL), image (NOT NULL)
# ======================================================

# Simple ZIP pattern for US "12345" or "12345-6789" (len <= 10 per model)
_US_ZIP_RE = re.compile(r"^\d{5}(?:-\d{4})?$")

class MyUserCreateSchema(Schema):
    # Create / PUT: require all NOT NULL columns
    first_name = fields.String(required=True)
    last_name  = fields.String(required=True)
    email      = fields.Email(required=True)
    gender     = fields.String(required=True)
    dob        = fields.Date(required=True)          # parses ISO-like strings to date
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
        # Soft validation: only enforce if it looks numeric-ish; otherwise allow
        if re.fullmatch(r"[0-9\-]+", v) and not _US_ZIP_RE.match(v):
            raise ValidationError("ZIP must be 12345 or 12345-6789.")

    @validates("image")
    def _v_image(self, v):
        if not v or not v.strip():
            raise ValidationError("Image path/URL cannot be empty.")
        if len(v) > 300:
            raise ValidationError("Image path too long (max 300).")

class MyUserUpdateSchema(Schema):
    # PATCH: all optional, but if provided must be valid
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
    dob        = fields.Date()                         # serialize as ISO date
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
# BlogPost Schemas (with added validators)
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

blog_post_out = BlogPostOutSchema()
blog_post_list_out = BlogPostOutSchema(many=True)

class BlogPostCreateSchema(Schema):
    title             = fields.String(required=True)
    slug              = fields.String(required=True)
    blog_cat_id       = fields.Integer(required=True)
    author_id         = fields.Integer(required=True)
    image             = fields.String(required=True)
    content_mongo_id  = fields.String(allow_none=True)

    @validates("title")
    def _v_title(self, v):
        if not v or not v.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def _v_slug(self, v):
        if not v or not v.strip():
            raise ValidationError("Slug cannot be empty.")
        if v != _slugify(v):
            raise ValidationError("Slug must be URL-safe (lowercase, hyphenated).")

    @validates("image")
    def _v_image(self, v):
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

    @validates("title")
    def _v_title(self, v):
        if v is not None and not v.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def _v_slug(self, v):
        if v is not None:
            if not v.strip():
                raise ValidationError("Slug cannot be empty.")
            if v != _slugify(v):
                raise ValidationError("Slug must be URL-safe (lowercase, hyphenated).")

    @validates("image")
    def _v_image(self, v):
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
    post_id = fields.Integer()

news_post_out = NewsPostOutSchema()
news_post_list_out = NewsPostOutSchema(many=True)

class NewsPostCreateSchema(Schema):
    post_id = fields.Integer(required=True)

class NewsPostUpdateSchema(Schema):
    post_id = fields.Integer()

news_post_create = NewsPostCreateSchema()
news_post_update = NewsPostUpdateSchema()

