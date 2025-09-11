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
    def validate_title(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def validate_slug(self, value, **kwargs):
        if not value or not value.strip():
            raise ValidationError("Slug cannot be empty.")
        if value != _slugify(value):
            raise ValidationError("Slug must be URL-safe (lowercase, hyphenated).")

class BlogCategoryUpdateSchema(Schema):
    title = fields.String(required=False)
    slug = fields.String(required=False)
    description = fields.String(required=False, allow_none=True)

    @validates("title")
    def validate_title(self, value, **kwargs):
        if value is not None and not value.strip():
            raise ValidationError("Title cannot be empty.")

    @validates("slug")
    def validate_slug(self, value, **kwargs):
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
    first_name     = fields.String(required=True)
    last_name      = fields.String(required=True)
    email          = fields.Email(required=True)
    gender         = fields.String(required=True)
    dob            = fields.Date(required=True)
    zip_code       = fields.String(required=True)
    city_state     = fields.String(required=False, allow_none=True)
    image          = fields.String(required=True)
    password       = fields.String(required=True, load_only=True)  # 🔑 plain-text input only
    is_admin       = fields.Boolean(load_default=False)
    is_member       = fields.Boolean(required=False)
    is_active      = fields.Boolean(load_default=True)

class MyUserUpdateSchema(Schema):
    first_name     = fields.String(required=False)
    last_name      = fields.String(required=False)
    email          = fields.Email(required=False)
    gender         = fields.String(required=False)
    dob            = fields.Date(required=False)
    zip_code       = fields.String(required=False)
    city_state     = fields.String(required=False, allow_none=True)
    image          = fields.String(required=False)
    password       = fields.String(required=False, load_only=True)  # allow password reset
    is_admin       = fields.Boolean(required=False)
    is_member       = fields.Boolean(required=False)
    is_active      = fields.Boolean(required=False)
    email_verified = fields.Boolean(required=False)

class MyUserOutSchema(Schema):
    my_user_id     = fields.Integer()
    first_name     = fields.String()
    last_name      = fields.String()
    email          = fields.String()
    gender         = fields.String()
    dob            = fields.Date()
    zip_code       = fields.String()
    city_state     = fields.String(allow_none=True)
    image          = fields.String()
    is_admin       = fields.Boolean()
    is_member       = fields.Boolean()
    is_active      = fields.Boolean()
    email_verified = fields.Boolean()
    created_at     = fields.DateTime(allow_none=True)
    updated_at     = fields.DateTime(allow_none=True)

my_user_out = MyUserOutSchema()
my_user_list_out = MyUserOutSchema(many=True)
my_user_create = MyUserCreateSchema()
my_user_update = MyUserUpdateSchema()

# ==============================
# BlogContent Schemas (SQL model)
# ==============================
class BlogContentOutSchema(Schema):
    blog_con_id = fields.Integer()
    post_id     = fields.Integer()
    yt_vid_id   = fields.String(allow_none=True)

    # Section 1
    section_1_title              = fields.String()
    section_1_paragraph_1        = fields.String()
    section_1_paragraph_2        = fields.String()
    section_1_paragraph_3        = fields.String()
    section_1_img                = fields.String(allow_none=True)
    section_1_link_internal      = fields.String(allow_none=True)
    section_1_link_external      = fields.String(allow_none=True)

    # Section 2
    section_2_title              = fields.String()
    section_2_paragraph_1        = fields.String()
    section_2_paragraph_2        = fields.String()
    section_2_paragraph_3        = fields.String()
    section_2_img                = fields.String(allow_none=True)
    section_2_link_internal      = fields.String(allow_none=True)
    section_2_link_external      = fields.String(allow_none=True)

    # Section 3
    section_3_title              = fields.String()
    section_3_paragraph_1        = fields.String()
    section_3_paragraph_2        = fields.String()
    section_3_paragraph_3        = fields.String()
    section_3_img                = fields.String(allow_none=True)
    section_3_link_internal      = fields.String(allow_none=True)
    section_3_link_external      = fields.String(allow_none=True)

    # Section 4
    section_4_title              = fields.String()
    section_4_paragraph_1        = fields.String()
    section_4_paragraph_2        = fields.String()
    section_4_paragraph_3        = fields.String()
    section_4_img                = fields.String(allow_none=True)
    section_4_link_internal      = fields.String(allow_none=True)
    section_4_link_external      = fields.String(allow_none=True)

    # Section 5
    section_5_title              = fields.String()
    section_5_paragraph_1        = fields.String()
    section_5_paragraph_2        = fields.String()
    section_5_paragraph_3        = fields.String()
    section_5_img                = fields.String(allow_none=True)
    section_5_link_internal      = fields.String(allow_none=True)
    section_5_link_external      = fields.String(allow_none=True)

    # Section 6 (conclusion)
    section_6_conclusion_title         = fields.String()
    section_6_conclusion_paragraph_1   = fields.String()
    section_6_conclusion_paragraph_2   = fields.String()
    section_6_conclusion_paragraph_3   = fields.String()
    section_6_conclusion_img           = fields.String(allow_none=True)
    section_6_conclusion_link_internal = fields.String(allow_none=True)
    section_6_conclusion_link_external = fields.String(allow_none=True)

    # Section 7 (assoc-press)
    section_7_assoc_press_title         = fields.String()
    section_7_assoc_press_paragraph_1   = fields.String()
    section_7_assoc_press_img           = fields.String(allow_none=True)
    section_7_assoc_press_link_internal = fields.String(allow_none=True)
    section_7_assoc_press_link_external = fields.String(allow_none=True)

    # FAQs
    faq_q_1 = fields.String()
    faq_a_1 = fields.String()
    faq_q_2 = fields.String()
    faq_a_2 = fields.String()
    faq_q_3 = fields.String()
    faq_a_3 = fields.String()
    faq_q_4 = fields.String(allow_none=True)
    faq_a_4 = fields.String(allow_none=True)
    faq_q_5 = fields.String(allow_none=True)
    faq_a_5 = fields.String(allow_none=True)
    faq_q_6 = fields.String(allow_none=True)
    faq_a_6 = fields.String(allow_none=True)

    created_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(allow_none=True)


blog_content_out = BlogContentOutSchema()
blog_content_list_out = BlogContentOutSchema(many=True)

class BlogContentCreateSchema(Schema):
    yt_vid_id = fields.String(required=False, allow_none=True)

    # Section 1 (required)
    section_1_title              = fields.String(required=True)
    section_1_paragraph_1        = fields.String(required=True)
    section_1_paragraph_2        = fields.String(required=True)
    section_1_paragraph_3        = fields.String(required=True)
    section_1_img                = fields.String(allow_none=True)
    section_1_link_internal      = fields.String(allow_none=True)
    section_1_link_external      = fields.String(allow_none=True)

    # Section 2 (required)
    section_2_title              = fields.String(required=True)
    section_2_paragraph_1        = fields.String(required=True)
    section_2_paragraph_2        = fields.String(required=True)
    section_2_paragraph_3        = fields.String(required=True)
    section_2_img                = fields.String(allow_none=True)
    section_2_link_internal      = fields.String(allow_none=True)
    section_2_link_external      = fields.String(allow_none=True)

    # Section 3 (required)
    section_3_title              = fields.String(required=True)
    section_3_paragraph_1        = fields.String(required=True)
    section_3_paragraph_2        = fields.String(required=True)
    section_3_paragraph_3        = fields.String(required=True)
    section_3_img                = fields.String(allow_none=True)
    section_3_link_internal      = fields.String(allow_none=True)
    section_3_link_external      = fields.String(allow_none=True)

    # Section 4 (required)
    section_4_title              = fields.String(required=True)
    section_4_paragraph_1        = fields.String(required=True)
    section_4_paragraph_2        = fields.String(required=True)
    section_4_paragraph_3        = fields.String(required=True)
    section_4_img                = fields.String(allow_none=True)
    section_4_link_internal      = fields.String(allow_none=True)
    section_4_link_external      = fields.String(allow_none=True)

    # Section 5 (required)
    section_5_title              = fields.String(required=True)
    section_5_paragraph_1        = fields.String(required=True)
    section_5_paragraph_2        = fields.String(required=True)
    section_5_paragraph_3        = fields.String(required=True)
    section_5_img                = fields.String(allow_none=True)
    section_5_link_internal      = fields.String(allow_none=True)
    section_5_link_external      = fields.String(allow_none=True)

    # Section 6 (conclusion, required)
    section_6_conclusion_title         = fields.String(required=True)
    section_6_conclusion_paragraph_1   = fields.String(required=True)
    section_6_conclusion_paragraph_2   = fields.String(required=True)
    section_6_conclusion_paragraph_3   = fields.String(required=True)
    section_6_conclusion_img           = fields.String(allow_none=True)
    section_6_conclusion_link_internal = fields.String(allow_none=True)
    section_6_conclusion_link_external = fields.String(allow_none=True)

    # Section 7 (assoc-press, required)
    section_7_assoc_press_title         = fields.String(required=True)
    section_7_assoc_press_paragraph_1   = fields.String(required=True)
    section_7_assoc_press_img           = fields.String(allow_none=True)
    section_7_assoc_press_link_internal = fields.String(allow_none=True)
    section_7_assoc_press_link_external = fields.String(allow_none=True)

    # FAQs (1–3 required; 4–6 optional)
    faq_q_1 = fields.String(required=True)
    faq_a_1 = fields.String(required=True)
    faq_q_2 = fields.String(required=True)
    faq_a_2 = fields.String(required=True)
    faq_q_3 = fields.String(required=True)
    faq_a_3 = fields.String(required=True)
    faq_q_4 = fields.String(allow_none=True)
    faq_a_4 = fields.String(allow_none=True)
    faq_q_5 = fields.String(allow_none=True)
    faq_a_5 = fields.String(allow_none=True)
    faq_q_6 = fields.String(allow_none=True)
    faq_a_6 = fields.String(allow_none=True)
blog_content_create = BlogContentCreateSchema()

class BlogContentUpdateSchema(Schema):
    yt_vid_id = fields.String(required=False, allow_none=True)

    # All fields optional for partial updates; if present, allow empty=None
    section_1_title              = fields.String()
    section_1_paragraph_1        = fields.String()
    section_1_paragraph_2        = fields.String()
    section_1_paragraph_3        = fields.String()
    section_1_img                = fields.String(allow_none=True)
    section_1_link_internal      = fields.String(allow_none=True)
    section_1_link_external      = fields.String(allow_none=True)

    section_2_title              = fields.String()
    section_2_paragraph_1        = fields.String()
    section_2_paragraph_2        = fields.String()
    section_2_paragraph_3        = fields.String()
    section_2_img                = fields.String(allow_none=True)
    section_2_link_internal      = fields.String(allow_none=True)
    section_2_link_external      = fields.String(allow_none=True)

    section_3_title              = fields.String()
    section_3_paragraph_1        = fields.String()
    section_3_paragraph_2        = fields.String()
    section_3_paragraph_3        = fields.String()
    section_3_img                = fields.String(allow_none=True)
    section_3_link_internal      = fields.String(allow_none=True)
    section_3_link_external      = fields.String(allow_none=True)

    section_4_title              = fields.String()
    section_4_paragraph_1        = fields.String()
    section_4_paragraph_2        = fields.String()
    section_4_paragraph_3        = fields.String()
    section_4_img                = fields.String(allow_none=True)
    section_4_link_internal      = fields.String(allow_none=True)
    section_4_link_external      = fields.String(allow_none=True)

    section_5_title              = fields.String()
    section_5_paragraph_1        = fields.String()
    section_5_paragraph_2        = fields.String()
    section_5_paragraph_3        = fields.String()
    section_5_img                = fields.String(allow_none=True)
    section_5_link_internal      = fields.String(allow_none=True)
    section_5_link_external      = fields.String(allow_none=True)

    section_6_conclusion_title         = fields.String()
    section_6_conclusion_paragraph_1   = fields.String()
    section_6_conclusion_paragraph_2   = fields.String()
    section_6_conclusion_paragraph_3   = fields.String()
    section_6_conclusion_img           = fields.String(allow_none=True)
    section_6_conclusion_link_internal = fields.String(allow_none=True)
    section_6_conclusion_link_external = fields.String(allow_none=True)

    section_7_assoc_press_title         = fields.String()
    section_7_assoc_press_paragraph_1   = fields.String()
    section_7_assoc_press_img           = fields.String(allow_none=True)
    section_7_assoc_press_link_internal = fields.String(allow_none=True)
    section_7_assoc_press_link_external = fields.String(allow_none=True)

    faq_q_1 = fields.String()
    faq_a_1 = fields.String()
    faq_q_2 = fields.String()
    faq_a_2 = fields.String()
    faq_q_3 = fields.String()
    faq_a_3 = fields.String()
    faq_q_4 = fields.String(allow_none=True)
    faq_a_4 = fields.String(allow_none=True)
    faq_q_5 = fields.String(allow_none=True)
    faq_a_5 = fields.String(allow_none=True)
    faq_q_6 = fields.String(allow_none=True)
    faq_a_6 = fields.String(allow_none=True)
blog_content_update = BlogContentUpdateSchema()





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
    # 👇 now strongly typed to SQL BlogContent fields
    content           = fields.Nested(BlogContentOutSchema, required=False)

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
    #content           = fields.Dict(required=False)
    # 👇 now strongly typed to SQL BlogContent fields
    content           = fields.Nested(BlogContentCreateSchema, required=False)

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

blog_post_create = BlogPostCreateSchema()

class BlogPostUpdateSchema(Schema):
    title             = fields.String()
    slug              = fields.String()
    blog_cat_id       = fields.Integer()
    author_id         = fields.Integer()
    image             = fields.String()
    content_mongo_id  = fields.String(allow_none=True)
    # ✅ allow partial updates that include content
    #content           = fields.Dict(required=False)
    # 👇 partial updates allowed
    content           = fields.Nested(BlogContentUpdateSchema, required=False)    

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
    def _v_views(self, v, **kwargs):
        if v is not None and v < 0:
            raise ValidationError("views cannot be negative.")

    @validates("likes")
    def _v_likes(self, v, **kwargs):
        if v is not None and v < 0:
            raise ValidationError("likes cannot be negative.")

    @validates("comments")
    def _v_comments(self, v, **kwargs):
        if v is not None and v < 0:
            raise ValidationError("comments cannot be negative.")

    @validates("shares")
    def _v_shares(self, v, **kwargs):
        if v is not None and v < 0:
            raise ValidationError("shares cannot be negative.")

class PostAnalyticsUpdateSchema(Schema):
    views    = fields.Integer()
    likes    = fields.Integer()
    comments = fields.Integer()
    shares   = fields.Integer()

    @validates("views")
    def _v_views(self, v, **kwargs):
        if v is not None and v < 0:
            raise ValidationError("views cannot be negative.")

    @validates("likes")
    def _v_likes(self, v, **kwargs):
        if v is not None and v < 0:
            raise ValidationError("likes cannot be negative.")

    @validates("comments")
    def _v_comments(self, v, **kwargs):
        if v is not None and v < 0:
            raise ValidationError("comments cannot be negative.")

    @validates("shares")
    def _v_shares(self, v, **kwargs):
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
