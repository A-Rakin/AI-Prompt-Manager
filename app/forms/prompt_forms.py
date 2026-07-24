from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

# ==============================================================================
# PromptForge - Prompt, Category, and Collection Forms
# ==============================================================================
# Defines forms for managing Prompts, custom Categories, and Collection Folders.
# ==============================================================================

# Popular AI platforms supported by default
PLATFORM_CHOICES = [
    ('ChatGPT', 'ChatGPT (OpenAI)'),
    ('Claude', 'Claude (Anthropic)'),
    ('Gemini', 'Gemini (Google)'),
    ('Copilot', 'Microsoft Copilot'),
    ('Grok', 'Grok (xAI)'),
    ('Midjourney', 'Midjourney'),
    ('Stable Diffusion', 'Stable Diffusion'),
    ('Custom', 'Other / Custom AI Model')
]

DIFFICULTY_CHOICES = [
    ('Beginner', 'Beginner (Simple One-shot)'),
    ('Intermediate', 'Intermediate (Structured / Contextual)'),
    ('Advanced', 'Advanced (Multi-step / System Prompt)')
]

LANGUAGE_CHOICES = [
    ('English', 'English'),
    ('Spanish', 'Spanish'),
    ('French', 'French'),
    ('German', 'German'),
    ('Chinese', 'Chinese'),
    ('Japanese', 'Japanese'),
    ('Python', 'Python (Code Prompt)'),
    ('JavaScript', 'JavaScript (Code Prompt)'),
    ('SQL', 'SQL (Database Prompt)'),
    ('Markdown', 'Markdown / Plain Text')
]

class PromptForm(FlaskForm):
    """
    Form for creating and updating AI prompts.
    """
    title = StringField(
        'Prompt Title',
        validators=[
            DataRequired(message="Title is required."),
            Length(max=150, message="Title cannot exceed 150 characters.")
        ],
        render_kw={"placeholder": "e.g. Senior Python Code Reviewer & Optimizer", "class": "form-control"}
    )
    description = StringField(
        'Short Description',
        validators=[Length(max=500, message="Description cannot exceed 500 characters.")],
        render_kw={"placeholder": "Briefly explain what this prompt does...", "class": "form-control"}
    )
    content = TextAreaField(
        'Prompt Content',
        validators=[DataRequired(message="Prompt content is required.")],
        render_kw={"placeholder": "Act as a Senior Python Developer with 10 years of experience...", "rows": 8, "class": "form-control code-font"}
    )
    platform = SelectField(
        'Target AI Platform',
        choices=PLATFORM_CHOICES,
        default='ChatGPT',
        render_kw={"class": "form-select"}
    )
    category_id = SelectField(
        'Category',
        coerce=int,
        render_kw={"class": "form-select"}
    )
    tags_input = StringField(
        'Tags (Comma Separated)',
        render_kw={"placeholder": "e.g. python, code-review, refactoring", "class": "form-control"}
    )
    language = SelectField(
        'Language',
        choices=LANGUAGE_CHOICES,
        default='English',
        render_kw={"class": "form-select"}
    )
    difficulty = SelectField(
        'Complexity Level',
        choices=DIFFICULTY_CHOICES,
        default='Intermediate',
        render_kw={"class": "form-select"}
    )
    is_pinned = BooleanField('Pin to top of list')
    is_favorite = BooleanField('Mark as favorite')
    submit = SubmitField('Save Prompt', render_kw={"class": "btn btn-primary"})


class CategoryForm(FlaskForm):
    """
    Form for creating custom user categories.
    """
    name = StringField(
        'Category Name',
        validators=[
            DataRequired(message="Category name is required."),
            Length(max=64, message="Category name must be under 64 characters.")
        ],
        render_kw={"placeholder": "e.g. Legal Analysis or Data Science", "class": "form-control"}
    )
    color = StringField(
        'Badge Accent Color',
        default="#6366F1",
        render_kw={"type": "color", "class": "form-control form-control-color"}
    )
    icon = StringField(
        'Font Awesome Icon Class',
        default="fa-folder",
        render_kw={"placeholder": "e.g. fa-gavel or fa-chart-bar", "class": "form-control"}
    )
    submit = SubmitField('Create Category', render_kw={"class": "btn btn-success"})


class CollectionForm(FlaskForm):
    """
    Form for creating collection folders to group prompts together.
    """
    name = StringField(
        'Collection Name',
        validators=[
            DataRequired(message="Collection name is required."),
            Length(max=100, message="Collection name must be under 100 characters.")
        ],
        render_kw={"placeholder": "e.g. Q3 Marketing Campaign or Freelance Work", "class": "form-control"}
    )
    description = StringField(
        'Description',
        validators=[Length(max=255, message="Description must be under 255 characters.")],
        render_kw={"placeholder": "Brief description of prompts contained in this collection folder", "class": "form-control"}
    )
    color = StringField(
        'Folder Color',
        default="#8B5CF6",
        render_kw={"type": "color", "class": "form-control form-control-color"}
    )
    icon = StringField(
        'Icon',
        default="fa-folder-open",
        render_kw={"placeholder": "e.g. fa-briefcase or fa-graduation-cap", "class": "form-control"}
    )
    submit = SubmitField('Save Collection', render_kw={"class": "btn btn-primary"})
