# app/api.py
from flask import Blueprint, request, jsonify, current_app
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from bson import ObjectId

from .models import db, BlogCategory, MyUser, BlogPost, NewsPost
from .schemas import (
    # BlogCategory
    blog_category_out,
    blog_category_list_out,
    blog_category_create,
    blog_category_update,
    # MyUser
    my_user_out,
    my_user_list_out,
    my_user_create,
    my_user_update,
    # BlogPost
    blog_post_out,
    blog_post_list_out,
    blog_post_create,
    blog_post_update,
    # NewsPost
    news_post_out,
    news_post_list_out,
    news_post_create,
    news_post_update,
)

api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

# -------------------------------
# Helpers
# -------------------------------
def _json_error(message, status=400):
    return jsonify({"error": message}), status

def _get_mongo():
    """Return the configured Mongo DB handle or None."""
    return getattr(current_app, "mongo_db", None)

def _mongo_collection():
    """Return the collection used for blog/news content, or None."""
    mongo = getattr(current_app, "mongo_db", None)
    return mongo["blog_content"] if mongo is not None else None

def _is_valid_objectid(s: str) -> bool:
    try:
        ObjectId(str(s))
        return True
    except Exception:
        return False

def _fetch_mongo_json(content_id):
    """Fetch and return raw JSON stored in Mongo by _id (string/ObjectId)."""
    col = _mongo_collection()
    if col is None or not content_id:  # ✅ avoid truth testing on Collection
        return None
    try:
        doc = col.find_one({"_id": ObjectId(str(content_id))})
        if not doc:
            return None
        doc.pop("_id", None)  # hide internal id
        return doc
    except Exception as e:
        current_app.logger.error(f"Error fetching MongoDB content: {e}")
        return None

def _insert_mongo_json(payload: dict):
    """Insert JSON payload into Mongo and return inserted_id as str."""
    col = _mongo_collection()
    if col is None:
        return None
    result = col.insert_one(payload or {})
    return str(result.inserted_id)

def _update_mongo_json(existing_id, payload: dict):
    """Update if existing_id valid; else insert new. Returns (content_id_str, created_new)."""
    col = _mongo_collection()
    if col is None:
        return None, False
    if existing_id and _is_valid_objectid(existing_id):
        oid = ObjectId(str(existing_id))
        col.update_one({"_id": oid}, {"$set": payload or {}}, upsert=False)
        return str(oid), False
    new_id = _insert_mongo_json(payload or {})
    return new_id, True

# ======================================================
# BlogCategory (CRUD)
# ======================================================
class BlogCategoryListAPI(MethodView):
    def get(self):
        q = request.args.get("q", type=str)
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)

        query = BlogCategory.query
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                db.or_(
                    BlogCategory.title.ilike(like),
                    BlogCategory.slug.ilike(like),
                    BlogCategory.description.ilike(like),
                )
            )
        paged = query.order_by(BlogCategory.title.asc()).paginate(page=page, per_page=per_page, error_out=False)
        data = blog_category_list_out.dump(paged.items)
        return jsonify({
            "items": data,
            "page": paged.page,
            "per_page": paged.per_page,
            "total": paged.total,
            "pages": paged.pages
        }), 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        errors = blog_category_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        cat = BlogCategory(**payload)
        db.session.add(cat)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Title or slug already exists.", 409)

        return blog_category_out.dump(cat), 201


class BlogCategoryItemAPI(MethodView):
    def get(self, cat_id: int):
        cat = BlogCategory.query.get_or_404(cat_id)
        return blog_category_out.dump(cat), 200

    def put(self, cat_id: int):
        payload = request.get_json(silent=True) or {}
        errors = blog_category_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        cat = BlogCategory.query.get_or_404(cat_id)
        cat.title = payload["title"]
        cat.slug = payload["slug"]
        cat.description = payload.get("description")

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Title or slug already exists.", 409)

        return blog_category_out.dump(cat), 200

    def patch(self, cat_id: int):
        payload = request.get_json(silent=True) or {}
        errors = blog_category_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        cat = BlogCategory.query.get_or_404(cat_id)
        if "title" in payload:
            cat.title = payload["title"]
        if "slug" in payload:
            cat.slug = payload["slug"]
        if "description" in payload:
            cat.description = payload["description"]

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Title or slug already exists.", 409)

        return blog_category_out.dump(cat), 200

    def delete(self, cat_id: int):
        cat = BlogCategory.query.get_or_404(cat_id)
        db.session.delete(cat)
        db.session.commit()
        return jsonify({"status": "deleted", "blog_cat_id": cat_id}), 200

# ======================================================
# MyUser (CRUD)
# ======================================================
class MyUserListAPI(MethodView):
    def get(self):
        q = request.args.get("q", type=str)
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)

        query = MyUser.query
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                db.or_(
                    MyUser.first_name.ilike(like),
                    MyUser.last_name.ilike(like),
                    MyUser.email.ilike(like),
                    MyUser.city_state.ilike(like),
                )
            )

        paged = query.order_by(MyUser.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        data = my_user_list_out.dump(paged.items)
        return jsonify({
            "items": data,
            "page": paged.page,
            "per_page": paged.per_page,
            "total": paged.total,
            "pages": paged.pages
        }), 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        errors = my_user_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        user = MyUser(**payload)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Could not create user (possible constraint error).", 409)

        return my_user_out.dump(user), 201


class MyUserItemAPI(MethodView):
    def get(self, user_id: int):
        user = MyUser.query.get_or_404(user_id)
        return my_user_out.dump(user), 200

    def put(self, user_id: int):
        payload = request.get_json(silent=True) or {}
        errors = my_user_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        user = MyUser.query.get_or_404(user_id)
        user.first_name = payload["first_name"]
        user.last_name  = payload["last_name"]
        user.email      = payload["email"]
        user.gender     = payload["gender"]
        user.dob        = payload["dob"]
        user.zip_code   = payload["zip_code"]
        user.city_state = payload.get("city_state")
        user.image      = payload["image"]

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Could not update user (constraint error).", 409)

        return my_user_out.dump(user), 200

    def patch(self, user_id: int):
        payload = request.get_json(silent=True) or {}
        errors = my_user_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        user = MyUser.query.get_or_404(user_id)
        for field in ["first_name", "last_name", "email", "gender", "dob", "zip_code", "city_state", "image"]:
            if field in payload:
                setattr(user, field, payload[field])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Could not update user (constraint error).", 409)

        return my_user_out.dump(user), 200

    def delete(self, user_id: int):
        user = MyUser.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"status": "deleted", "my_user_id": user_id}), 200

# ======================================================
# BlogPost (CRUD + Mongo content)
# ======================================================
class BlogPostListAPI(MethodView):
    def get(self):
        q = request.args.get("q", type=str)
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")

        query = BlogPost.query
        if q:
            like = f"%{q.strip()}%"
            query = query.filter(
                db.or_(
                    BlogPost.title.ilike(like),
                    BlogPost.slug.ilike(like),
                )
            )

        paged = query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        items = blog_post_list_out.dump(paged.items)

        # Hide content_mongo_id from list view (public)
        for item in items:
            item.pop("content_mongo_id", None)

        if include_content:
            for i, row in enumerate(paged.items):
                content = _fetch_mongo_json(row.content_mongo_id)
                if content is not None:
                    items[i]["content"] = content

        return jsonify({
            "items": items,
            "page": paged.page,
            "per_page": paged.per_page,
            "total": paged.total,
            "pages": paged.pages
        }), 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        errors = blog_post_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        # Ensure FK exist
        if not BlogCategory.query.get(payload["blog_cat_id"]):
            return _json_error("blog_cat_id not found.", 404)
        if not MyUser.query.get(payload["author_id"]):
            return _json_error("author_id not found.", 404)

        # Optional content
        content = payload.pop("content", None)
        if content is not None:
            if _mongo_collection() is None:
                return _json_error("MongoDB is not configured but 'content' was provided.", 503)
            content_id = _insert_mongo_json(content)
            payload["content_mongo_id"] = content_id

        post = BlogPost(**payload)
        db.session.add(post)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Title or slug already exists.", 409)

        data = blog_post_out.dump(post)
        # Embed content on create if present (or fetch if content_mongo_id was provided)
        if content is not None:
            data["content"] = content
        elif post.content_mongo_id:
            embedded = _fetch_mongo_json(post.content_mongo_id)
            if embedded is not None:
                data["content"] = embedded
        return data, 201


class BlogPostItemAPI(MethodView):
    def get(self, post_id: int):
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")
        post = BlogPost.query.get_or_404(post_id)
        data = blog_post_out.dump(post)
        if include_content:
            content = _fetch_mongo_json(post.content_mongo_id)
            if content is not None:
                data["content"] = content
        return data, 200

    def put(self, post_id: int):
        payload = request.get_json(silent=True) or {}
        errors = blog_post_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        if not BlogCategory.query.get(payload["blog_cat_id"]):
            return _json_error("blog_cat_id not found.", 404)
        if not MyUser.query.get(payload["author_id"]):
            return _json_error("author_id not found.", 404)

        post = BlogPost.query.get_or_404(post_id)

        # Content handling (replace or create)
        content = payload.pop("content", None)
        if content is not None:
            if _mongo_collection() is None:
                return _json_error("MongoDB is not configured but 'content' was provided.", 503)
            new_id, _ = _update_mongo_json(post.content_mongo_id, content)
            post.content_mongo_id = new_id

        post.title       = payload["title"]
        post.slug        = payload["slug"]
        post.blog_cat_id = payload["blog_cat_id"]
        post.author_id   = payload["author_id"]
        post.image       = payload["image"]

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Title or slug already exists.", 409)

        data = blog_post_out.dump(post)
        if content is not None:
            data["content"] = content
        elif post.content_mongo_id:
            embedded = _fetch_mongo_json(post.content_mongo_id)
            if embedded is not None:
                data["content"] = embedded
        return data, 200

    def patch(self, post_id: int):
        payload = request.get_json(silent=True) or {}
        errors = blog_post_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        post = BlogPost.query.get_or_404(post_id)

        if "blog_cat_id" in payload and not BlogCategory.query.get(payload["blog_cat_id"]):
            return _json_error("blog_cat_id not found.", 404)
        if "author_id" in payload and not MyUser.query.get(payload["author_id"]):
            return _json_error("author_id not found.", 404)

        # Optional content update
        content = payload.pop("content", None)
        if content is not None:
            if _mongo_collection() is None:
                return _json_error("MongoDB is not configured but 'content' was provided.", 503)
            new_id, _ = _update_mongo_json(post.content_mongo_id, content)
            post.content_mongo_id = new_id

        for field in ["title", "slug", "blog_cat_id", "author_id", "image", "content_mongo_id"]:
            if field in payload:
                setattr(post, field, payload[field])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Title or slug already exists.", 409)

        data = blog_post_out.dump(post)
        if content is not None:
            data["content"] = content
        elif post.content_mongo_id:
            embedded = _fetch_mongo_json(post.content_mongo_id)
            if embedded is not None:
                data["content"] = embedded
        return data, 200

    def delete(self, post_id: int):
        post = BlogPost.query.get_or_404(post_id)
        # Best-effort cleanup
        col = _mongo_collection()
        if post.content_mongo_id and col is not None and _is_valid_objectid(post.content_mongo_id):
            try:
                col.delete_one({"_id": ObjectId(post.content_mongo_id)})
            except Exception:
                pass
        db.session.delete(post)
        db.session.commit()
        return jsonify({"status": "deleted", "post_id": post_id}), 200

# ======================================================
# NewsPost (1:1 with BlogPost)
# ======================================================
class NewsPostListAPI(MethodView):
    def get(self):
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")

        query = NewsPost.query.join(BlogPost, NewsPost.post_id == BlogPost.post_id)
        paged = query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        items = []
        for news in paged.items:
            bp = news.post
            row = blog_post_out.dump(bp)
            row.pop("content_mongo_id", None)  # ✅ hide from public list view
            if include_content:
                content = _fetch_mongo_json(bp.content_mongo_id)
                if content is not None:
                    row["content"] = content
            items.append(row)

        return jsonify({
            "items": items,
            "page": paged.page,
            "per_page": paged.per_page,
            "total": paged.total,
            "pages": paged.pages
        }), 200

    def post(self):
        """Create a NewsPost row tied to an existing BlogPost.post_id."""
        payload = request.get_json(silent=True) or {}
        errors = news_post_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        post_id = payload["post_id"]
        bp = BlogPost.query.get(post_id)
        if not bp:
            return _json_error("BlogPost not found for given post_id.", 404)

        if NewsPost.query.get(post_id):
            return _json_error("NewsPost already exists for this post_id.", 409)

        news = NewsPost(post_id=post_id)
        db.session.add(news)
        db.session.commit()

        data = blog_post_out.dump(bp)
        embedded = _fetch_mongo_json(bp.content_mongo_id)
        if embedded is not None:
            data["content"] = embedded
        return data, 201


class NewsPostItemAPI(MethodView):
    def get(self, post_id: int):
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")
        news = NewsPost.query.get_or_404(post_id)
        bp = news.post
        data = blog_post_out.dump(bp)
        if include_content:
            content = _fetch_mongo_json(bp.content_mongo_id)
            if content is not None:
                data["content"] = content
        return data, 200

    def put(self, post_id: int):
        payload = request.get_json(silent=True) or {}
        errors = news_post_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        # Ensure exists
        news = NewsPost.query.get_or_404(post_id)
        bp = news.post
        data = blog_post_out.dump(bp)
        embedded = _fetch_mongo_json(bp.content_mongo_id)
        if embedded is not None:
            data["content"] = embedded
        return data, 200

    def patch(self, post_id: int):
        payload = request.get_json(silent=True) or {}
        errors = news_post_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        news = NewsPost.query.get_or_404(post_id)
        bp = news.post
        data = blog_post_out.dump(bp)
        embedded = _fetch_mongo_json(bp.content_mongo_id)
        if embedded is not None:
            data["content"] = embedded
        return data, 200

    def delete(self, post_id: int):
        news = NewsPost.query.get_or_404(post_id)
        db.session.delete(news)
        db.session.commit()
        return jsonify({"status": "deleted", "news_post_id": post_id}), 200

# -------------------------------
# Route Registration
# -------------------------------
# BlogCategory
api_bp.add_url_rule(
    "/blog-categories",
    view_func=BlogCategoryListAPI.as_view("blog_category_list"),
    methods=["GET", "POST"],
)
api_bp.add_url_rule(
    "/blog-categories/<int:cat_id>",
    view_func=BlogCategoryItemAPI.as_view("blog_category_item"),
    methods=["GET", "PUT", "PATCH", "DELETE"],
)

# MyUser
api_bp.add_url_rule(
    "/users",
    view_func=MyUserListAPI.as_view("user_list"),
    methods=["GET", "POST"],
)
api_bp.add_url_rule(
    "/users/<int:user_id>",
    view_func=MyUserItemAPI.as_view("user_item"),
    methods=["GET", "PUT", "PATCH", "DELETE"],
)

# BlogPost
api_bp.add_url_rule(
    "/blog-posts",
    view_func=BlogPostListAPI.as_view("blog_post_list"),
    methods=["GET", "POST"],
)
api_bp.add_url_rule(
    "/blog-posts/<int:post_id>",
    view_func=BlogPostItemAPI.as_view("blog_post_item"),
    methods=["GET", "PUT", "PATCH", "DELETE"],
)

# NewsPost
api_bp.add_url_rule(
    "/news-posts",
    view_func=NewsPostListAPI.as_view("news_post_list"),
    methods=["GET", "POST"],
)
api_bp.add_url_rule(
    "/news-posts/<int:post_id>",
    view_func=NewsPostItemAPI.as_view("news_post_item"),
    methods=["GET", "PUT", "PATCH", "DELETE"],
)
