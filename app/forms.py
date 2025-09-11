# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileField, FileAllowed

# ---------- BlogPost forms ----------

class BlogPostBaseForm(FlaskForm):
    title       = StringField("Title", validators=[DataRequired(), Length(max=255)])
    slug        = StringField("Slug", validators=[DataRequired(), Length(max=255)])
    blog_cat_id = SelectField("Category", coerce=int, validators=[DataRequired()])
    author_id   = SelectField("Author",   coerce=int, validators=[DataRequired()])

class BlogPostCreateForm(BlogPostBaseForm):
    # BlogPost.image is NOT NULL in the model, so require on CREATE
    image  = FileField("Image", validators=[DataRequired(), FileAllowed(["png","jpg","jpeg","webp","gif"])])
    submit = SubmitField("Create")

class BlogPostUpdateForm(BlogPostBaseForm):
    # On UPDATE, a post already has an image; uploading a new one is optional
    image  = FileField("Replace Image", validators=[Optional(), FileAllowed(["png","jpg","jpeg","webp","gif"])])
    submit = SubmitField("Save Changes")

# ---------- BlogContent form ----------
# Field names mirror model columns 1:1 so we can commit directly.

MAX_STR = 300

class BlogContentForm(FlaskForm):
    yt_vid_id = StringField("YouTube Video ID", validators=[Optional(), Length(max=20)])

    # ===== Section 1 (required text) =====
    section_1_title         = StringField("Section 1 Title", validators=[DataRequired(), Length(max=255)])
    section_1_paragraph_1   = TextAreaField("Section 1 ¶1", validators=[DataRequired()])
    section_1_paragraph_2   = TextAreaField("Section 1 ¶2", validators=[DataRequired()])
    section_1_paragraph_3   = TextAreaField("Section 1 ¶3", validators=[DataRequired()])
    section_1_img           = StringField("Section 1 Image", validators=[Optional(), Length(max=MAX_STR)])
    section_1_link_internal = StringField("Section 1 Link (Internal)", validators=[Optional(), Length(max=MAX_STR)])
    section_1_link_external = StringField("Section 1 Link (External)", validators=[Optional(), Length(max=MAX_STR)])

    # ===== Section 2 (required text) =====
    section_2_title         = StringField("Section 2 Title", validators=[DataRequired(), Length(max=255)])
    section_2_paragraph_1   = TextAreaField("Section 2 ¶1", validators=[DataRequired()])
    section_2_paragraph_2   = TextAreaField("Section 2 ¶2", validators=[DataRequired()])
    section_2_paragraph_3   = TextAreaField("Section 2 ¶3", validators=[DataRequired()])
    section_2_img           = StringField("Section 2 Image", validators=[Optional(), Length(max=MAX_STR)])
    section_2_link_internal = StringField("Section 2 Link (Internal)", validators=[Optional(), Length(max=MAX_STR)])
    section_2_link_external = StringField("Section 2 Link (External)", validators=[Optional(), Length(max=MAX_STR)])

    # ===== Section 3 (required text) =====
    section_3_title         = StringField("Section 3 Title", validators=[DataRequired(), Length(max=255)])
    section_3_paragraph_1   = TextAreaField("Section 3 ¶1", validators=[DataRequired()])
    section_3_paragraph_2   = TextAreaField("Section 3 ¶2", validators=[DataRequired()])
    section_3_paragraph_3   = TextAreaField("Section 3 ¶3", validators=[DataRequired()])
    section_3_img           = StringField("Section 3 Image", validators=[Optional(), Length(max=MAX_STR)])
    section_3_link_internal = StringField("Section 3 Link (Internal)", validators=[Optional(), Length(max=MAX_STR)])
    section_3_link_external = StringField("Section 3 Link (External)", validators=[Optional(), Length(max=MAX_STR)])

    # ===== Section 4 (required text) =====
    section_4_title         = StringField("Section 4 Title", validators=[DataRequired(), Length(max=255)])
    section_4_paragraph_1   = TextAreaField("Section 4 ¶1", validators=[DataRequired()])
    section_4_paragraph_2   = TextAreaField("Section 4 ¶2", validators=[DataRequired()])
    section_4_paragraph_3   = TextAreaField("Section 4 ¶3", validators=[DataRequired()])
    section_4_img           = StringField("Section 4 Image", validators=[Optional(), Length(max=MAX_STR)])
    section_4_link_internal = StringField("Section 4 Link (Internal)", validators=[Optional(), Length(max=MAX_STR)])
    section_4_link_external = StringField("Section 4 Link (External)", validators=[Optional(), Length(max=MAX_STR)])

    # ===== Section 5 (required text) =====
    section_5_title         = StringField("Section 5 Title", validators=[DataRequired(), Length(max=255)])
    section_5_paragraph_1   = TextAreaField("Section 5 ¶1", validators=[DataRequired()])
    section_5_paragraph_2   = TextAreaField("Section 5 ¶2", validators=[DataRequired()])
    section_5_paragraph_3   = TextAreaField("Section 5 ¶3", validators=[DataRequired()])
    section_5_img           = StringField("Section 5 Image", validators=[Optional(), Length(max=MAX_STR)])
    section_5_link_internal = StringField("Section 5 Link (Internal)", validators=[Optional(), Length(max=MAX_STR)])
    section_5_link_external = StringField("Section 5 Link (External)", validators=[Optional(), Length(max=MAX_STR)])

    # ===== Section 6 (conclusion, required) =====
    section_6_conclusion_title         = StringField("Conclusion Title", validators=[DataRequired(), Length(max=255)])
    section_6_conclusion_paragraph_1   = TextAreaField("Conclusion ¶1", validators=[DataRequired()])
    section_6_conclusion_paragraph_2   = TextAreaField("Conclusion ¶2", validators=[DataRequired()])
    section_6_conclusion_paragraph_3   = TextAreaField("Conclusion ¶3", validators=[DataRequired()])
    section_6_conclusion_img           = StringField("Conclusion Image", validators=[Optional(), Length(max=MAX_STR)])
    section_6_conclusion_link_internal = StringField("Conclusion Link (Internal)", validators=[Optional(), Length(max=MAX_STR)])
    section_6_conclusion_link_external = StringField("Conclusion Link (External)", validators=[Optional(), Length(max=MAX_STR)])

    # ===== Section 7 (assoc-press, required) =====
    section_7_assoc_press_title         = StringField("Assoc. Press Title", validators=[DataRequired(), Length(max=255)])
    section_7_assoc_press_paragraph_1   = TextAreaField("Assoc. Press ¶1", validators=[DataRequired()])
    section_7_assoc_press_img           = StringField("Assoc. Press Image", validators=[Optional(), Length(max=MAX_STR)])
    section_7_assoc_press_link_internal = StringField("Assoc. Press Link (Internal)", validators=[Optional(), Length(max=MAX_STR)])
    section_7_assoc_press_link_external = StringField("Assoc. Press Link (External)", validators=[Optional(), Length(max=MAX_STR)])

    # ===== Section 8 (FAQs) =====
    faq_q_1 = TextAreaField("FAQ Q1", validators=[DataRequired()])
    faq_a_1 = TextAreaField("FAQ A1", validators=[DataRequired()])
    faq_q_2 = TextAreaField("FAQ Q2", validators=[DataRequired()])
    faq_a_2 = TextAreaField("FAQ A2", validators=[DataRequired()])
    faq_q_3 = TextAreaField("FAQ Q3", validators=[DataRequired()])
    faq_a_3 = TextAreaField("FAQ A3", validators=[DataRequired()])
    faq_q_4 = TextAreaField("FAQ Q4", validators=[Optional()])
    faq_a_4 = TextAreaField("FAQ A4", validators=[Optional()])
    faq_q_5 = TextAreaField("FAQ Q5", validators=[Optional()])
    faq_a_5 = TextAreaField("FAQ A5", validators=[Optional()])
    faq_q_6 = TextAreaField("FAQ Q6", validators=[Optional()])
    faq_a_6 = TextAreaField("FAQ A6", validators=[Optional()])

    submit = SubmitField("Save Content")

    # Optional helper so routes can do: bc.content = form.as_content_dict()
    def as_content_dict(self) -> dict:
        fields = [
            "yt_vid_id",
            # s1
            "section_1_title","section_1_paragraph_1","section_1_paragraph_2","section_1_paragraph_3",
            "section_1_img","section_1_link_internal","section_1_link_external",
            # s2
            "section_2_title","section_2_paragraph_1","section_2_paragraph_2","section_2_paragraph_3",
            "section_2_img","section_2_link_internal","section_2_link_external",
            # s3
            "section_3_title","section_3_paragraph_1","section_3_paragraph_2","section_3_paragraph_3",
            "section_3_img","section_3_link_internal","section_3_link_external",
            # s4
            "section_4_title","section_4_paragraph_1","section_4_paragraph_2","section_4_paragraph_3",
            "section_4_img","section_4_link_internal","section_4_link_external",
            # s5
            "section_5_title","section_5_paragraph_1","section_5_paragraph_2","section_5_paragraph_3",
            "section_5_img","section_5_link_internal","section_5_link_external",
            # s6 conclusion
            "section_6_conclusion_title","section_6_conclusion_paragraph_1","section_6_conclusion_paragraph_2","section_6_conclusion_paragraph_3",
            "section_6_conclusion_img","section_6_conclusion_link_internal","section_6_conclusion_link_external",
            # s7 assoc press
            "section_7_assoc_press_title","section_7_assoc_press_paragraph_1",
            "section_7_assoc_press_img","section_7_assoc_press_link_internal","section_7_assoc_press_link_external",
            # FAQs
            "faq_q_1","faq_a_1","faq_q_2","faq_a_2","faq_q_3","faq_a_3",
            "faq_q_4","faq_a_4","faq_q_5","faq_a_5","faq_q_6","faq_a_6",
        ]
        return {k: getattr(self, k).data for k in fields}
