"""
Flask-Admin web interface for Food Diary Bot database management
"""
import os
import logging
from pathlib import Path
from flask import Flask, redirect, url_for, request
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()

class Meal(Base):
    """SQLAlchemy model for meals table"""
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String, nullable=True)
    meal_type = Column(String, nullable=True)
    ingredients = Column(String, nullable=True)
    calories = Column(Integer, nullable=True)
    message = Column(String, nullable=False)
    photo_path = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f'<Meal {self.id}: {self.username or self.user_id} - {self.message[:30]}>'


class SecureAdminIndexView(AdminIndexView):
    """Custom admin index view with authentication check and statistics"""
    
    def __init__(self, *args, **kwargs):
        self.db_session = kwargs.pop('session', None)
        super(SecureAdminIndexView, self).__init__(*args, **kwargs)
    
    @expose('/')
    def index(self):
        if not self.is_authenticated():
            return redirect(url_for('admin.login_view'))
        
        # Get database statistics
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        total_meals = self.db_session.query(func.count(Meal.id)).scalar() or 0
        total_users = self.db_session.query(func.count(func.distinct(Meal.user_id))).scalar() or 0
        recent_meals = self.db_session.query(Meal).order_by(Meal.timestamp.desc()).limit(5).all()
        
        # Calculate today's meals
        today = datetime.now().date()
        meals_today = self.db_session.query(func.count(Meal.id)).filter(
            func.date(Meal.timestamp) == today
        ).scalar() or 0
        
        # Calculate this week's meals
        week_ago = datetime.now() - timedelta(days=7)
        meals_this_week = self.db_session.query(func.count(Meal.id)).filter(
            Meal.timestamp >= week_ago
        ).scalar() or 0
        
        return self.render(
            'admin/custom_index.html',
            total_meals=total_meals,
            total_users=total_users,
            meals_today=meals_today,
            meals_this_week=meals_this_week,
            recent_meals=recent_meals
        )
    
    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # BasicAuth handles the actual authentication
        return redirect(url_for('admin.index'))
    
    def is_authenticated(self):
        auth = request.authorization
        if not auth:
            return False
        return True


class MealModelView(ModelView):
    """Custom ModelView for Meal with enhanced features"""
    
    # Column display configuration
    column_list = ['id', 'user_id', 'username', 'meal_type', 'ingredients', 'calories', 'message', 'photo_path', 'timestamp']
    column_searchable_list = ['username', 'message', 'user_id', 'ingredients']
    column_filters = ['user_id', 'username', 'meal_type', 'timestamp']
    column_sortable_list = ['id', 'user_id', 'username', 'meal_type', 'calories', 'timestamp']
    column_default_sort = ('timestamp', True)  # Sort by timestamp DESC
    
    # Form configuration
    form_columns = ['user_id', 'username', 'meal_type', 'ingredients', 'calories', 'message', 'photo_path', 'timestamp']
    
    # Pagination
    page_size = 50
    can_set_page_size = True
    
    # Enable export
    can_export = True
    export_types = ['csv', 'xlsx']
    
    # Column formatters
    column_formatters = {
        'message': lambda v, c, m, p: m.message[:50] + '...' if len(m.message) > 50 else m.message,
        'photo_path': lambda v, c, m, p: Path(m.photo_path).name if m.photo_path else 'No photo'
    }
    
    # Column labels
    column_labels = {
        'user_id': 'User ID',
        'username': 'Username',
        'message': 'Meal Description',
        'photo_path': 'Photo',
        'timestamp': 'Date & Time'
    }
    
    # Column descriptions
    column_descriptions = {
        'user_id': 'Telegram User ID',
        'username': 'Telegram Username',
        'message': 'Meal description or notes',
        'photo_path': 'Path to meal photo (relative)',
        'timestamp': 'When the meal was recorded'
    }
    
    def is_accessible(self):
        """Check if admin panel is accessible (BasicAuth will handle auth)"""
        return True


def create_app():
    """Create and configure Flask application"""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('ADMIN_SECRET_KEY', 'dev-secret-key-please-change')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'  # Bootstrap theme
    
    # Basic Authentication
    app.config['BASIC_AUTH_USERNAME'] = os.environ.get('ADMIN_USERNAME', 'admin')
    app.config['BASIC_AUTH_PASSWORD'] = os.environ.get('ADMIN_PASSWORD', 'admin')
    app.config['BASIC_AUTH_FORCE'] = True
    
    basic_auth = BasicAuth(app)
    
    # Database setup
    db_path = os.environ.get('DB_PATH', 'data/food_diary.db')
    database_url = f'sqlite:///{db_path}'
    
    # Ensure data directory exists
    Path('data').mkdir(exist_ok=True)
    
    engine = create_engine(
        database_url,
        connect_args={'check_same_thread': False},
        echo=False
    )
    
    # Create session
    db_session = scoped_session(sessionmaker(bind=engine))
    Base.query = db_session.query_property()
    
    # Create tables if they don't exist (they should already exist from bot.py)
    Base.metadata.create_all(bind=engine)
    
    # Initialize Flask-Admin
    admin = Admin(
        app,
        name='Food Diary Admin',
        template_mode='bootstrap4',
        index_view=SecureAdminIndexView(name='Home', session=db_session),
        base_template='admin/base.html'
    )
    
    # Add views
    admin.add_view(MealModelView(Meal, db_session, name='Meals', endpoint='meals'))
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()
    
    @app.route('/')
    def index():
        """Redirect root to admin panel"""
        return redirect(url_for('admin.index'))
    
    logger.info(f"Flask-Admin initialized with database: {db_path}")
    logger.info(f"Admin username: {app.config['BASIC_AUTH_USERNAME']}")
    
    return app


def main():
    """Run the Flask application"""
    app = create_app()
    
    # Get configuration from environment
    host = os.environ.get('ADMIN_HOST', '0.0.0.0')
    port = int(os.environ.get('ADMIN_PORT', 5000))
    debug = os.environ.get('ADMIN_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Food Diary Admin Panel on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
