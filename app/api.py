from flask import Blueprint, request, jsonify, current_app, url_for
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_, text
from bson import ObjectId

from .models import db, BlogCategory, MyUser, BlogPost, NewsPost, NewsMain, PostAnalytics
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
    # NewsMain
    news_main_out,
    news_main_list_out,
    news_main_create,
    news_main_update,
    # PostAnalytics
    post_analytics_out,
    post_analytics_list_out,
    post_analytics_create,
    post_analytics_update,
    # Optional combined
    blog_post_with_analytics_out,
    blog_post_with_analytics_list_out,
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
    if col is None or not content_id:
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

def _news_main_post(nm: NewsMain):
    """
    Safely resolve the related BlogPost for a NewsMain row.
    Uses the relationship if present on the model; falls back to querying by post_id.
    """
    bp = getattr(nm, "post", None)
    if bp is not None:
        return bp
    if nm.post_id is not None:
        return BlogPost.query.get(nm.post_id)
    return None

def _analytics_dict(pa: PostAnalytics | None):
    """Return a small dict of analytics counters (or zeroes)."""
    if not pa:
        return {"views": 0, "likes": 0, "comments": 0, "shares": 0}
    return {
        "views": pa.views or 0,
        "likes": pa.likes or 0,
        "comments": pa.comments or 0,
        "shares": pa.shares or 0,
    }

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
        include_analytics = request.args.get("include_analytics", default="false").lower() in ("1", "true", "yes")

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

        # If caller wants analytics inline and you kept the relationship on the model,
        # you can serialize with the combined schema. Otherwise use the base schema.
        if include_analytics:
            items = blog_post_with_analytics_list_out.dump(paged.items)
        else:
            items = blog_post_list_out.dump(paged.items)

        # Hide content_mongo_id from list view (public)
        for item in items:
            item.pop("content_mongo_id", None)

        # Add browser-ready image URL
        for i, row in enumerate(paged.items):
            items[i]["image_url"] = url_for("static", filename=row.image) if row.image else None

            # If you didn't use combined schema, optionally tack on analytics here:
            if not include_analytics:
                items[i]["analytics"] = _analytics_dict(getattr(row, "analytics", None))

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
        data["image_url"] = url_for("static", filename=post.image) if post.image else None

        # Embed content on create if present (or fetch if content_mongo_id was provided)
        if content is not None:
            data["content"] = content
        elif post.content_mongo_id:
            embedded = _fetch_mongo_json(post.content_mongo_id)
            if embedded is not None:
                data["content"] = embedded

        # Attach analytics skeleton (0s) for convenience
        data["analytics"] = _analytics_dict(getattr(post, "analytics", None))
        return data, 201


class BlogPostItemAPI(MethodView):
    def get(self, post_id: int):
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")
        include_analytics = request.args.get("include_analytics", default="false").lower() in ("1", "true", "yes")

        post = BlogPost.query.get_or_404(post_id)
        data = (blog_post_with_analytics_out.dump(post)
                if include_analytics
                else blog_post_out.dump(post))
        data["image_url"] = url_for("static", filename=post.image) if post.image else None

        if not include_analytics:
            data["analytics"] = _analytics_dict(getattr(post, "analytics", None))

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
        data["image_url"] = url_for("static", filename=post.image) if post.image else None
        if content is not None:
            data["content"] = content
        elif post.content_mongo_id:
            embedded = _fetch_mongo_json(post.content_mongo_id)
            if embedded is not None:
                data["content"] = embedded
        data["analytics"] = _analytics_dict(getattr(post, "analytics", None))
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
        data["image_url"] = url_for("static", filename=post.image) if post.image else None
        if content is not None:
            data["content"] = content
        elif post.content_mongo_id:
            embedded = _fetch_mongo_json(post.content_mongo_id)
            if embedded is not None:
                data["content"] = embedded
        data["analytics"] = _analytics_dict(getattr(post, "analytics", None))
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
        include_analytics = request.args.get("include_analytics", default="false").lower() in ("1", "true", "yes")

        query = NewsPost.query.join(BlogPost, NewsPost.post_id == BlogPost.post_id)
        paged = query.order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        items = []
        for news in paged.items:
            bp = news.post
            row = blog_post_out.dump(bp)
            row.pop("content_mongo_id", None)  # hide from public list view
            # include browser-ready image URL
            row["image_url"] = url_for("static", filename=bp.image) if bp.image else None
            if include_content:
                content = _fetch_mongo_json(bp.content_mongo_id)
                if content is not None:
                    row["content"] = content
            # analytics (inline or zeroes)
            if include_analytics:
                row.update(_analytics_dict(getattr(bp, "analytics", None)))
            else:
                row["analytics"] = _analytics_dict(getattr(bp, "analytics", None))
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
        data["image_url"] = url_for("static", filename=bp.image) if bp.image else None
        embedded = _fetch_mongo_json(bp.content_mongo_id)
        if embedded is not None:
            data["content"] = embedded
        data["analytics"] = _analytics_dict(getattr(bp, "analytics", None))
        return data, 201


class NewsPostItemAPI(MethodView):
    def get(self, post_id: int):
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")
        include_analytics = request.args.get("include_analytics", default="false").lower() in ("1", "true", "yes")

        news = NewsPost.query.get_or_404(post_id)
        bp = news.post
        data = blog_post_out.dump(bp)
        data["image_url"] = url_for("static", filename=bp.image) if bp.image else None

        if include_content:
            content = _fetch_mongo_json(bp.content_mongo_id)
            if content is not None:
                data["content"] = content

        if include_analytics:
            data.update(_analytics_dict(getattr(bp, "analytics", None)))
        else:
            data["analytics"] = _analytics_dict(getattr(bp, "analytics", None))

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
        data["image_url"] = url_for("static", filename=bp.image) if bp.image else None
        embedded = _fetch_mongo_json(bp.content_mongo_id)
        if embedded is not None:
            data["content"] = embedded
        data["analytics"] = _analytics_dict(getattr(bp, "analytics", None))
        return data, 200

    def patch(self, post_id: int):
        payload = request.get_json(silent=True) or {}
        errors = news_post_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        news = NewsPost.query.get_or_404(post_id)
        bp = news.post
        data = blog_post_out.dump(bp)
        data["image_url"] = url_for("static", filename=bp.image) if bp.image else None
        embedded = _fetch_mongo_json(bp.content_mongo_id)
        if embedded is not None:
            data["content"] = embedded
        data["analytics"] = _analytics_dict(getattr(bp, "analytics", None))
        return data, 200

    def delete(self, post_id: int):
        news = NewsPost.query.get_or_404(post_id)
        db.session.delete(news)
        db.session.commit()
        return jsonify({"status": "deleted", "news_post_id": post_id}), 200

# ---------------------------------------------------------
# NewsPostReadNextAPI
# Returns up to the next N news posts for the "Read Next" carousel.
# Excludes the current post_id and orders by BlogPost.created_at (desc).
# ---------------------------------------------------------
class NewsPostReadNextAPI(MethodView):
    def get(self, post_id: int):
        limit = request.args.get("limit", default=3, type=int)
        include_content = request.args.get("include_content", default="false").lower() in ("1", "true", "yes")
        include_analytics = request.args.get("include_analytics", default="false").lower() in ("1", "true", "yes")

        # Ensure the current news post exists (pk = BlogPost.post_id)
        _ = NewsPost.query.get_or_404(post_id)

        # Other news posts, newest first (pull fields from BlogPost)
        rows = (
            BlogPost.query
            .join(NewsPost, NewsPost.post_id == BlogPost.post_id)
            .filter(BlogPost.post_id != post_id)
            .order_by(BlogPost.created_at.desc())
            .limit(limit)
            .all()
        )

        items = []
        for bp in rows:
            row = blog_post_out.dump(bp)
            row.pop("content_mongo_id", None)  # hide internal id
            row["image_url"] = url_for("static", filename=bp.image) if bp.image else None

            if include_content:
                content = _fetch_mongo_json(bp.content_mongo_id)
                if content is not None:
                    row["content"] = content

            if include_analytics:
                row.update(_analytics_dict(getattr(bp, "analytics", None)))
            else:
                row["analytics"] = _analytics_dict(getattr(bp, "analytics", None))

            items.append(row)

        return jsonify({"items": items, "count": len(items)}), 200

# ---------------------------------------------------------
# NewsPostRelatedAPI
# Returns up to N related news posts (same category as current),
# excluding the current post_id. Results are BlogPost-shaped objects
# (with image_url and analytics), optionally with content.
# ---------------------------------------------------------
class NewsPostRelatedAPI(MethodView):
    def get(self, post_id: int):
        limit = request.args.get("limit", default=4, type=int)
        include_content = request.args.get("include_content", default="false").lower() in ("1", "true", "yes")
        include_analytics = request.args.get("include_analytics", default="false").lower() in ("1", "true", "yes")

        # Ensure current news post exists and fetch its BlogPost (for category)
        news = NewsPost.query.get_or_404(post_id)
        bp_current = news.post
        cat_id = bp_current.blog_cat_id

        # Other news posts in the SAME category (exclude current), newest first
        rows = (
            BlogPost.query
            .join(NewsPost, NewsPost.post_id == BlogPost.post_id)
            .filter(BlogPost.post_id != post_id)
            .filter(BlogPost.blog_cat_id == cat_id)
            .order_by(BlogPost.created_at.desc())
            .limit(limit)
            .all()
        )

        items = []
        for bp in rows:
            row = blog_post_out.dump(bp)
            row.pop("content_mongo_id", None)
            row["image_url"] = url_for("static", filename=bp.image) if bp.image else None

            if include_content:
                content = _fetch_mongo_json(bp.content_mongo_id)
                if content is not None:
                    row["content"] = content

            if include_analytics:
                row.update(_analytics_dict(getattr(bp, "analytics", None)))
            else:
                row["analytics"] = _analytics_dict(getattr(bp, "analytics", None))

            items.append(row)

        return jsonify({"items": items, "count": len(items)}), 200

# ======================================================
# NewsMain (windowed "main story" selections)
# ======================================================
class NewsMainListAPI(MethodView):
    def get(self):
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=20, type=int)
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")
        active_only = request.args.get("active", default=None)

        query = NewsMain.query

        # Optional: filter current active window when active=1/true
        if active_only is not None and str(active_only).lower() in ("1", "true", "yes"):
            today = func.current_date()
            query = query.filter(and_(NewsMain.start_date <= today, NewsMain.end_date >= today))

        query = query.join(BlogPost, NewsMain.post_id == BlogPost.post_id)

        paged = query.order_by(NewsMain.start_date.desc(), NewsMain.created_at.desc()) \
                     .paginate(page=page, per_page=per_page, error_out=False)

        items = []
        for nm in paged.items:
            bp = _news_main_post(nm)  # robust resolution even if relationship missing
            nm_row = news_main_out.dump(nm)
            post_row = blog_post_out.dump(bp) if bp else {}
            post_row.pop("content_mongo_id", None)  # hide from public list view
            # add browser-ready image URL for nested post
            if bp and bp.image:
                post_row["image_url"] = url_for("static", filename=bp.image)
            if include_content and bp:
                content = _fetch_mongo_json(bp.content_mongo_id)
                if content is not None:
                    post_row["content"] = content
            # tack on analytics for nested post
            post_row["analytics"] = _analytics_dict(getattr(bp, "analytics", None)) if bp else _analytics_dict(None)
            items.append({
                "news_main": nm_row,
                "post": post_row,
            })

        return jsonify({
            "items": items,
            "page": paged.page,
            "per_page": paged.per_page,
            "total": paged.total,
            "pages": paged.pages
        }), 200

    def post(self):
        payload = request.get_json(silent=True) or {}
        errors = news_main_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        # Ensure BlogPost exists
        post_id = payload["post_id"]
        bp = BlogPost.query.get(post_id)
        if not bp:
            return _json_error("BlogPost not found for given post_id.", 404)

        nm = NewsMain(
            post_id=post_id,
            start_date=payload["start_date"],
            end_date=payload["end_date"],
            notes=payload.get("notes"),
        )
        db.session.add(nm)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # Likely UNIQUE window or EXCLUDE overlap violation
            return _json_error("Could not create NewsMain (constraint violation: overlapping window or duplicate).", 409)

        data = {
            "news_main": news_main_out.dump(nm),
            "post": blog_post_out.dump(bp)
        }
        # include image_url & analytics on nested post
        if bp and bp.image:
            data["post"]["image_url"] = url_for("static", filename=bp.image)
        data["post"]["analytics"] = _analytics_dict(getattr(bp, "analytics", None))
        return data, 201


class NewsMainItemAPI(MethodView):
    def get(self, news_main_id: int):
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")
        nm = NewsMain.query.get_or_404(news_main_id)
        bp = _news_main_post(nm)
        nm_row = news_main_out.dump(nm)
        post_row = blog_post_out.dump(bp) if bp else {}
        if bp and bp.image:
            post_row["image_url"] = url_for("static", filename=bp.image)
        if include_content and bp:
            content = _fetch_mongo_json(bp.content_mongo_id)
            if content is not None:
                post_row["content"] = content
        post_row["analytics"] = _analytics_dict(getattr(bp, "analytics", None)) if bp else _analytics_dict(None)
        return {"news_main": nm_row, "post": post_row}, 200

    def put(self, news_main_id: int):
        payload = request.get_json(silent=True) or {}
        errors = news_main_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        nm = NewsMain.query.get_or_404(news_main_id)

        # Allow re-pointing and window updates
        if "post_id" in payload and payload["post_id"] is not None:
            bp = BlogPost.query.get(payload["post_id"])
            if not bp:
                return _json_error("BlogPost not found for given post_id.", 404)
            nm.post_id = payload["post_id"]

        if "start_date" in payload and payload["start_date"] is not None:
            nm.start_date = payload["start_date"]
        if "end_date" in payload and payload["end_date"] is not None:
            nm.end_date = payload["end_date"]
        if "notes" in payload:
            nm.notes = payload["notes"]

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Could not update NewsMain (constraint violation: overlapping window or duplicate).", 409)

        bp = _news_main_post(nm)
        post_row = blog_post_out.dump(bp) if bp else {}
        if bp and bp.image:
            post_row["image_url"] = url_for("static", filename=bp.image)
        post_row["analytics"] = _analytics_dict(getattr(bp, "analytics", None)) if bp else _analytics_dict(None)
        return {"news_main": news_main_out.dump(nm), "post": post_row}, 200

    def patch(self, news_main_id: int):
        # Same behavior as PUT for partial updates
        return self.put(news_main_id)

    def delete(self, news_main_id: int):
        nm = NewsMain.query.get_or_404(news_main_id)
        db.session.delete(nm)
        db.session.commit()
        return jsonify({"status": "deleted", "news_main_id": news_main_id}), 200

# ======================================================
# PostAnalytics (CRUD)
# ======================================================
class PostAnalyticsListAPI(MethodView):
    def get(self):
        """List analytics rows (paginated)."""
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=50, type=int)

        paged = PostAnalytics.query.order_by(PostAnalytics.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        data = post_analytics_list_out.dump(paged.items)
        return jsonify({
            "items": data,
            "page": paged.page,
            "per_page": paged.per_page,
            "total": paged.total,
            "pages": paged.pages
        }), 200

    def post(self):
        """Create analytics row for a post (1:1)."""
        payload = request.get_json(silent=True) or {}
        errors = post_analytics_create.validate(payload)
        if errors:
            return _json_error(errors, 400)

        post_id = payload["post_id"]
        if not BlogPost.query.get(post_id):
            return _json_error("BlogPost not found for given post_id.", 404)

        # enforce uniqueness at app level too
        if PostAnalytics.query.filter_by(post_id=post_id).first():
            return _json_error("Analytics already exists for this post_id.", 409)

        pa = PostAnalytics(
            post_id=post_id,
            views=payload.get("views", 0),
            likes=payload.get("likes", 0),
            comments=payload.get("comments", 0),
            shares=payload.get("shares", 0),
        )
        db.session.add(pa)
        db.session.commit()
        return post_analytics_out.dump(pa), 201


class PostAnalyticsItemAPI(MethodView):
    def get(self, post_id: int):
        pa = PostAnalytics.query.filter_by(post_id=post_id).first()
        if not pa:
            return _json_error("Analytics row not found.", 404)
        return post_analytics_out.dump(pa), 200

    def patch(self, post_id: int):
        payload = request.get_json(silent=True) or {}
        errors = post_analytics_update.validate(payload)
        if errors:
            return _json_error(errors, 400)

        pa = PostAnalytics.query.filter_by(post_id=post_id).first()
        if not pa:
            return _json_error("Analytics row not found.", 404)

        for field in ["views", "likes", "comments", "shares"]:
            if field in payload and payload[field] is not None:
                setattr(pa, field, payload[field])

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _json_error("Could not update analytics.", 409)

        return post_analytics_out.dump(pa), 200

    def delete(self, post_id: int):
        pa = PostAnalytics.query.filter_by(post_id=post_id).first()
        if not pa:
            return _json_error("Analytics row not found.", 404)
        db.session.delete(pa)
        db.session.commit()
        return jsonify({"status": "deleted", "post_id": post_id}), 200

# ======================================================
# Most-read (from SQL Views) — read-only helpers
# ======================================================
class MostReadBlogAPI(MethodView):
    def get(self):
        """Return rows from atlLocal_db.v_most_read_blog_posts (read-only)."""
        sql = text("""
            SELECT post_id, title, slug, image, blog_cat_id, author_id,
                   created_at, views, likes, comments, shares
            FROM atlLocal_db.v_most_read_blog_posts
        """)
        rows = db.session.execute(sql).mappings().all()
        # add image_url for convenience
        out = []
        for r in rows:
            row = dict(r)
            row["image_url"] = url_for("static", filename=row["image"]) if row.get("image") else None
            out.append(row)
        return jsonify({"items": out, "count": len(out)}), 200


class MostReadNewsAPI(MethodView):
    def get(self):
        """Return rows from atlLocal_db.v_most_read_news_posts (read-only)."""
        sql = text("""
            SELECT post_id, title, slug, image, blog_cat_id, author_id,
                   created_at, views, likes, comments, shares
            FROM atlLocal_db.v_most_read_news_posts
        """)
        rows = db.session.execute(sql).mappings().all()
        out = []
        for r in rows:
            row = dict(r)
            row["image_url"] = url_for("static", filename=row["image"]) if row.get("image") else None
            out.append(row)
        return jsonify({"items": out, "count": len(out)}), 200


class LatestNewsAPI(MethodView):
    def get(self):
        """
        Return latest news posts as FULL post objects (like /api/v1/news-posts),
        enriched with Mongo 'content', 'image_url', and 'analytics'.
        """
        include_content = request.args.get("include_content", default="true").lower() in ("1", "true", "yes")
        include_analytics = request.args.get("include_analytics", default="false").lower() in ("1", "true", "yes")
        per_page = request.args.get("per_page", type=int)

        # Pull the latest post IDs from the SQL view (already ordered in the view).
        sql = text("""SELECT post_id FROM atllocal_db.v_latest_news_posts""")
        rows = db.session.execute(sql).mappings().all()
        post_ids = [r["post_id"] for r in rows]

        # Respect ?per_page= if provided (helps the /news page show top N)
        if per_page is not None and per_page > 0:
            post_ids = post_ids[:per_page]

        items = []
        for pid in post_ids:
            bp = BlogPost.query.get(pid)
            if not bp:
                continue

            # Serialize like NewsPost list items (BlogPost-shaped)
            row = blog_post_out.dump(bp)
            row.pop("content_mongo_id", None)  # hide internal id

            # Image URL for browser
            row["image_url"] = url_for("static", filename=bp.image) if bp.image else None

            # Mongo content (optional)
            if include_content:
                content = _fetch_mongo_json(bp.content_mongo_id)
                if content is not None:
                    row["content"] = content

            # Analytics
            if include_analytics:
                row.update(_analytics_dict(getattr(bp, "analytics", None)))
            else:
                row["analytics"] = _analytics_dict(getattr(bp, "analytics", None))

            items.append(row)

        return jsonify({"items": items, "count": len(items)}), 200

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

# Read-Next
api_bp.add_url_rule(
    "/news/<int:post_id>/read-next",
    view_func=NewsPostReadNextAPI.as_view("news_post_read_next"),
    methods=["GET"],
)

# Related (same category)
api_bp.add_url_rule(
    "/news/<int:post_id>/related",
    view_func=NewsPostRelatedAPI.as_view("news_post_related"),
    methods=["GET"],
)


# NewsMain
api_bp.add_url_rule(
    "/news-main",
    view_func=NewsMainListAPI.as_view("news_main_list"),
    methods=["GET", "POST"],
)
api_bp.add_url_rule(
    "/news-main/<int:news_main_id>",
    view_func=NewsMainItemAPI.as_view("news_main_item"),
    methods=["GET", "PUT", "PATCH", "DELETE"],
)

# PostAnalytics
api_bp.add_url_rule(
    "/post-analytics",
    view_func=PostAnalyticsListAPI.as_view("post_analytics_list"),
    methods=["GET", "POST"],
)
api_bp.add_url_rule(
    "/post-analytics/<int:post_id>",
    view_func=PostAnalyticsItemAPI.as_view("post_analytics_item"),
    methods=["GET", "PATCH", "DELETE"],
)

# Most-read (views)
api_bp.add_url_rule(
    "/analytics/most-read/blog",
    view_func=MostReadBlogAPI.as_view("most_read_blog"),
    methods=["GET"],
)
api_bp.add_url_rule(
    "/analytics/most-read/news",
    view_func=MostReadNewsAPI.as_view("most_read_news"),
    methods=["GET"],
)
api_bp.add_url_rule(
    "/analytics/latest-news",
    view_func=LatestNewsAPI.as_view("latest_news"),
    methods=["GET"],
)
