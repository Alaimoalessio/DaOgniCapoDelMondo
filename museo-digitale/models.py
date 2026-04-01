"""
Database models for Da ogni capo del mondo - Digital Museum
SQLAlchemy ORM models for managing the museum collection
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for many-to-many relationship between Items and Materials
item_materials = db.Table('item_materials',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
    db.Column('material_id', db.Integer, db.ForeignKey('material.id'), primary_key=True)
)


class Category(db.Model):
    """Categories for museum objects (Militaria, Cerimoniale, Abbigliamento, etc.)"""
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('Item', back_populates='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Region(db.Model):
    """Geographic regions (Asia, Africa, Europa, Americhe, Oceania)"""
    __tablename__ = 'region'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    continent = db.Column(db.String(50))
    description = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('Item', back_populates='region', lazy='dynamic')
    
    def __repr__(self):
        return f'<Region {self.name}>'


class Material(db.Model):
    """Materials used in objects (Oro, Argento, Tessuto, Legno, etc.)"""
    __tablename__ = 'material'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Material {self.name}>'


class Era(db.Model):
    """Historical periods (Medievale, Rinascimentale, Moderno, etc.)"""
    __tablename__ = 'era'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    year_start = db.Column(db.Integer)
    year_end = db.Column(db.Integer)
    description = db.Column(db.Text)
    
    # Relationships
    items = db.relationship('Item', back_populates='era', lazy='dynamic')
    
    def __repr__(self):
        return f'<Era {self.name}>'


class Item(db.Model):
    """Core table for museum objects"""
    __tablename__ = 'item'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    historical_context = db.Column(db.Text)
    
    # Dating
    year_from = db.Column(db.Integer)
    year_to = db.Column(db.Integer)
    
    # Origin
    provenance = db.Column(db.String(200))
    
    # Media
    image_url = db.Column(db.String(500))
    
    # Conservation
    conservation_state = db.Column(db.String(50))  # Ottimo, Buono, Discreto, Restaurato
    
    # Management
    acquisition_date = db.Column(db.Date)
    acquisition_cost = db.Column(db.Numeric(12, 2))  # Cost when acquired
    notes = db.Column(db.Text)
    is_visible = db.Column(db.Boolean, default=True)  # Show/hide from public
    view_count = db.Column(db.Integer, default=0)  # Track views
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    era_id = db.Column(db.Integer, db.ForeignKey('era.id'))
    
    # Relationships
    category = db.relationship('Category', back_populates='items')
    region = db.relationship('Region', back_populates='items')
    era = db.relationship('Era', back_populates='items')
    materials = db.relationship('Material', secondary=item_materials, lazy='subquery',
                               backref=db.backref('items', lazy=True))
    
    def __repr__(self):
        return f'<Item {self.title}>'
    
    def to_dict(self):
        """Convert item to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'historical_context': self.historical_context,
            'year_from': self.year_from,
            'year_to': self.year_to,
            'provenance': self.provenance,
            'image_url': self.image_url,
            'conservation_state': self.conservation_state,
            'category': self.category.name if self.category else None,
            'region': self.region.name if self.region else None,
            'era': self.era.name if self.era else None,
            'materials': [m.name for m in self.materials]
        }


class User(UserMixin, db.Model):
    """User model for family/private area authentication"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    private_notes = db.relationship('PrivateNote', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    loans = db.relationship('Loan', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class PrivateNote(db.Model):
    """Private notes for items (family only)"""
    __tablename__ = 'private_note'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='private_notes')
    item = db.relationship('Item')
    
    def __repr__(self):
        return f'<PrivateNote {self.id}>'


class Loan(db.Model):
    """Loan tracking for items"""
    __tablename__ = 'loan'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    borrower = db.Column(db.String(200), nullable=False)
    borrower_contact = db.Column(db.String(200))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    expected_return_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='active')  # active, returned, overdue
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='loans')
    item = db.relationship('Item')
    
    def __repr__(self):
        return f'<Loan {self.id}>'


# Association table for many-to-many relationship between Items and Exhibitions
item_exhibitions = db.Table('item_exhibitions',
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'), primary_key=True),
    db.Column('exhibition_id', db.Integer, db.ForeignKey('exhibition.id'), primary_key=True)
)


class Exhibition(db.Model):
    """Exhibitions/Shows where items are displayed"""
    __tablename__ = 'exhibition'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))  # Museum, Villa, etc.
    address = db.Column(db.String(500))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='planned')  # planned, active, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('Item', secondary=item_exhibitions, lazy='subquery',
                           backref=db.backref('exhibitions', lazy=True))
    
    def __repr__(self):
        return f'<Exhibition {self.title}>'


class ItemImage(db.Model):
    """Multiple images for items"""
    __tablename__ = 'item_image'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))
    is_primary = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    item = db.relationship('Item', backref='images')
    
    def __repr__(self):
        return f'<ItemImage {self.id}>'


class ItemDocument(db.Model):
    """Documents, videos, and other media for items"""
    __tablename__ = 'item_document'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50))  # pdf, video, audio, etc.
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    item = db.relationship('Item', backref='documents')
    
    def __repr__(self):
        return f'<ItemDocument {self.id}>'


class ItemValuation(db.Model):
    """Valuations and insurance information for items"""
    __tablename__ = 'item_valuation'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    estimated_value = db.Column(db.Numeric(12, 2))  # Value in EUR
    currency = db.Column(db.String(10), default='EUR')
    valuation_date = db.Column(db.Date, nullable=False)
    valuator = db.Column(db.String(200))  # Who made the valuation
    insurance_value = db.Column(db.Numeric(12, 2))
    insurance_company = db.Column(db.String(200))
    insurance_policy_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    item = db.relationship('Item', backref='valuations')
    
    def __repr__(self):
        return f'<ItemValuation {self.id}>'


class ItemQRCode(db.Model):
    """QR codes for items"""
    __tablename__ = 'item_qrcode'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False, unique=True)
    qr_code_url = db.Column(db.String(500), nullable=False)  # Path to QR code image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    item = db.relationship('Item', backref='qrcode', uselist=False)
    
    def __repr__(self):
        return f'<ItemQRCode {self.id}>'


class Notification(db.Model):
    """Notifications and reminders"""
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # loan_due, maintenance, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    related_item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    related_loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    related_item = db.relationship('Item')
    related_loan = db.relationship('Loan')
    
    def __repr__(self):
        return f'<Notification {self.id}>'
