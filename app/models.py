import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# ==============================================================================
# PromptForge - Database Models (SQLAlchemy ORM)
# ==============================================================================
# In web applications, an Object-Relational Mapper (ORM) maps database tables to
# Python classes. Instead of writing raw SQL queries (like `SELECT * FROM users`),
# we interact with database records directly as Python objects.
#
# Key Concepts Explained:
# 1. Primary Key: A unique identifier for each database record (e.g. `id`).
# 2. Foreign Key: A column that references the Primary Key of another table,
#    creating a relationship between two tables (e.g., `user_id` points to `users.id`).
# 3. One-to-Many Relationship: One user can create many prompts, but each prompt
#    belongs to only one user.
# 4. Many-to-Many Relationship: A prompt can have multiple tags, and a single tag
#    can belong to multiple prompts. This requires a "Junction Table" (or Association Table)
#    to connect them without duplicating data.
# 5. UserMixin: A helper class from Flask-Login providing standard methods like `is_authenticated`,
#    `is_active`, `is_anonymous`, and `get_id()`.
# 6. Soft Delete (Archiving): Rather than destroying data completely with `DELETE FROM`,
#    we set a `status` field to 'archived'. This allows users to recover deleted prompts easily.
# ==============================================================================

# Initialize the SQLAlchemy database instance
db = SQLAlchemy()

# ------------------------------------------------------------------------------
# Junction (Association) Tables for Many-to-Many Relationships
# ------------------------------------------------------------------------------

# Association table linking Prompts and Tags
# A prompt can have 0 to many tags, and a tag can belong to 0 to many prompts.
prompt_tags = db.Table(
    'prompt_tags',
    db.Column('prompt_id', db.Integer, db.ForeignKey('prompts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

# Association table linking Prompts and Collections (Folders)
# Users can organize prompts into multiple collection folders (e.g., Work, Personal, Research).
prompt_collections = db.Table(
    'prompt_collections',
    db.Column('prompt_id', db.Integer, db.ForeignKey('prompts.id', ondelete='CASCADE'), primary_key=True),
    db.Column('collection_id', db.Integer, db.ForeignKey('collections.id', ondelete='CASCADE'), primary_key=True)
)


# ------------------------------------------------------------------------------
# Database Model Classes
# ------------------------------------------------------------------------------

class User(db.Model, UserMixin):
    """
    User model representing registered accounts in PromptForge.
    Stores account credentials, profile details, and UI theme preferences.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile attributes
    bio = db.Column(db.String(500), nullable=True, default="")
    avatar = db.Column(db.String(200), nullable=True, default="default_avatar.png")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # User UI Customization preferences (Notion / Linear style customization)
    theme_preference = db.Column(db.String(20), default="dark")  # 'dark' or 'light'
    accent_color = db.Column(db.String(20), default="#6366F1")    # Default Indigo/Purple accent
    font_size = db.Column(db.String(20), default="medium")        # 'small', 'medium', 'large'
    compact_mode = db.Column(db.Boolean, default=False)           # Tighter paddings for power users
    animations_enabled = db.Column(db.Boolean, default=True)      # Toggle AOS animations

    # ORM Relationships: Connecting User to their owned entities
    prompts = db.relationship('Prompt', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='creator', lazy='dynamic', cascade='all, delete-orphan')
    collections = db.relationship('Collection', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    copy_histories = db.relationship('CopyHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """
        Hashes plain-text passwords securely using PBKDF2/SHA256 algorithm before storing.
        Never store raw passwords in a database!
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifies an incoming plain-text password against the stored cryptographic hash.
        Returns True if matched, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User username='{self.username}' email='{self.email}'>"


class Category(db.Model):
    """
    Category model for organizing prompts into high-level domains
    (e.g., Programming, Writing, Marketing, Design, Education, Research, Business, Productivity).
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    slug = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(20), default="#6366F1")  # Hex color code for badges
    icon = db.Column(db.String(50), default="fa-folder")  # Font Awesome icon class name
    is_system = db.Column(db.Boolean, default=False)     # True for default categories available to all
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Prompts belonging to this category
    prompts = db.relationship('Prompt', backref='category', lazy='dynamic')

    def __repr__(self):
        return f"<Category name='{self.name}'>"


class Tag(db.Model):
    """
    Tag model allowing flexible, keyword-based search and filtering.
    (e.g., #code-review, #creative-writing, #seo, #python).
    """
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"<Tag name='{self.name}'>"


class Collection(db.Model):
    """
    Collection model representing user-created folder structures (e.g., Work, Personal, University).
    Enables drag-and-drop prompt organization.
    """
    __tablename__ = 'collections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    color = db.Column(db.String(20), default="#8B5CF6")
    icon = db.Column(db.String(50), default="fa-layer-group")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Collection name='{self.name}'>"


class Prompt(db.Model):
    """
    Prompt model representing individual AI prompts saved by users.
    Contains rich fields like title, content, target platform, language, copy statistics,
    pinned & favorite states, and soft-delete archiving status.
    """
    __tablename__ = 'prompts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    
    # Target AI Platform (e.g., ChatGPT, Claude, Gemini, Copilot, Grok, Midjourney, Stable Diffusion)
    platform = db.Column(db.String(50), nullable=False, default="ChatGPT")
    
    # Additional Metadata
    language = db.Column(db.String(30), default="English")       # Programming language or natural language
    difficulty = db.Column(db.String(20), default="Intermediate") # Beginner, Intermediate, Advanced
    
    # Status & Flags
    status = db.Column(db.String(20), default="active")          # 'active' or 'archived' (soft delete)
    is_pinned = db.Column(db.Boolean, default=False)             # Pinned to top of lists
    is_favorite = db.Column(db.Boolean, default=False)           # Quick access in favorites section
    
    # Productivity Analytics
    copy_count = db.Column(db.Integer, default=0)                # Incremented every time user copies prompt
    last_copied_at = db.Column(db.DateTime, nullable=True)       # Timestamp of recent copy action
    
    # Foreign Keys & Timestamps
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    tags = db.relationship('Tag', secondary=prompt_tags, backref=db.backref('prompts', lazy='select'))
    collections = db.relationship('Collection', secondary=prompt_collections, backref=db.backref('collections', lazy='select'))
    activity_logs = db.relationship('ActivityLog', backref='prompt', lazy='dynamic', cascade='all, delete-orphan')
    copy_histories = db.relationship('CopyHistory', backref='prompt', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        """
        Converts the Prompt model instance into a Python dictionary.
        This is crucial for serializing data when returning JSON responses from REST APIs.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'platform': self.platform,
            'language': self.language,
            'difficulty': self.difficulty,
            'status': self.status,
            'is_pinned': self.is_pinned,
            'is_favorite': self.is_favorite,
            'copy_count': self.copy_count,
            'last_copied_at': self.last_copied_at.isoformat() if self.last_copied_at else None,
            'category': self.category.name if self.category else 'Uncategorized',
            'category_color': self.category.color if self.category else '#64748B',
            'tags': [tag.name for tag in self.tags],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f"<Prompt title='{self.title}' platform='{self.platform}'>"


class ActivityLog(db.Model):
    """
    ActivityLog model for recording user actions over time.
    Powers the Dashboard "Activity Timeline" widget.
    (e.g., Created prompt 'SEO Blog Generator', Copied prompt 'Python Refactor', Favorited prompt).
    """
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(50), nullable=False)  # 'created', 'edited', 'copied', 'favorited', 'archived'
    details = db.Column(db.String(255), nullable=True)  # Additional context description
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<ActivityLog action='{self.action}' user_id={self.user_id}>"


class CopyHistory(db.Model):
    """
    CopyHistory model tracking every time a prompt is copied to clipboard.
    Used for calculating copy velocity and most popular prompt trends.
    """
    __tablename__ = 'copy_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False)
    copied_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<CopyHistory prompt_id={self.prompt_id} copied_at={self.copied_at}>"
