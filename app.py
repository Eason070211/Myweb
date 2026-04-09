from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# Rate limiting
login_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 300
ADMIN_SECRET_KEY = 'eason123'



def check_rate_limit(ip):
    current_time = time.time()
    if ip in login_attempts:
        attempts, first_time = login_attempts[ip]
        if current_time - first_time < LOCKOUT_TIME and attempts >= MAX_ATTEMPTS:
            return True, "Too many failed attempts. Please try again in 5 minutes."
        elif current_time - first_time >= LOCKOUT_TIME:
            del login_attempts[ip]
    return False, None

def record_failed_attempt(ip):
    current_time = time.time()
    if ip not in login_attempts:
        login_attempts[ip] = [1, current_time]
    else:
        attempts, _ = login_attempts[ip]
        login_attempts[ip] = [attempts + 1, current_time]

def reset_attempts(ip):
    if ip in login_attempts:
        del login_attempts[ip]

def generate_captcha():
    a = secrets.randbelow(20) + 1
    b = secrets.randbelow(20) + 1
    operator = secrets.choice(['+', '-'])
    if operator == '+':
        answer = a + b
        question = f"{a} + {b} = ?"
    else:
        answer = a - b
        question = f"{a} - {b} = ?"
    return question, str(answer)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60))
    is_admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(100), default='Exploring')
    bio = db.Column(db.Text, default='Explorer | Content Creator | Lifelong Learner\nCreating digital footprints across the web.')
    theme_enabled = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(300))
    author = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.Integer, default=lambda: int(time.time()))
    category = db.Column(db.String(50), default='随笔')
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery',
        backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.Integer, default=lambda: int(time.time()))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    count = db.Column(db.Integer, default=0)

@app.context_processor
def inject_stats():
    recent = Post.query.order_by(Post.created_at.desc()).limit(10).all()
    admin = User.query.filter_by(username='admin').first()
    return dict(
        total_posts=Post.query.count(),
        total_categories=len(get_all_categories()),
        total_tags=len(get_all_tags()),
        recent_posts=recent,
        admin_status=admin.status if admin else 'Exploring',
        admin_bio=admin.bio if admin else 'Explorer | Content Creator | Lifelong Learner\nCreating digital footprints across the web.',
        theme_enabled=admin.theme_enabled if admin else False
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def get_all_tags():
    tags = Tag.query.all()
    return [{'name': t.name, 'count': len(t.posts)} for t in tags]

def get_all_categories():
    categories = db.session.query(Post.category, db.func.count(Post.id)).group_by(Post.category).all()
    if not categories:
        return [{'name': '随笔', 'count': 0}, {'name': '技术', 'count': 0}]
    return [{'name': c[0], 'count': c[1]} for c in categories]

def get_archives():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    archives = {}
    for p in posts:
        year = time.strftime('%Y', time.localtime(p.created_at))
        if year not in archives:
            archives[year] = []
        archives[year].append({'title': p.title, 'date': time.strftime('%Y-%m-%d', time.localtime(p.created_at)), 'id': p.id})
    return [{'date': k, 'posts': v} for k, v in sorted(archives.items(), reverse=True)]

# Routes
@app.route('/')
def index():
    category_filter = request.args.get('category', None)
    tag_filter = request.args.get('tag', None)
    search_query = request.args.get('search', None)
    
    posts = Post.query
    
    if category_filter:
        posts = posts.filter_by(category=category_filter)
    if tag_filter:
        tag = Tag.query.filter_by(name=tag_filter).first()
        if tag:
            post_ids = [p.id for p in tag.posts]
            posts = posts.filter(Post.id.in_(post_ids)) if post_ids else Post.query.filter(db.false())
        else:
            posts = posts.filter(db.false())
    
    if search_query:
        all_posts = posts.all()
        
        def calc_score(post):
            title = post.title or ""
            content = post.content or ""
            text = (title + content).lower()
            query = search_query.lower()
            
            if not query:
                return 0, 0
            
            exact_count = text.count(query)
            if exact_count > 0:
                score = 10000 + exact_count * 1000
            else:
                matched_chars = 0
                for char in query:
                    if char in text:
                        matched_chars += 1
                if matched_chars > 0:
                    score = matched_chars * 100
                else:
                    score = 0
            
            return score, post.created_at
        
        scored = [(p, calc_score(p)) for p in all_posts]
        scored.sort(key=lambda x: (-x[1][0], -x[1][1]))
        posts = [p[0] for p in scored if p[1][0] > 0]
    else:
        posts = posts.order_by(Post.created_at.desc()).all()
    
    posts_data = [{
        'id': p.id, 'title': p.title, 'summary': p.summary or p.content[:100],
        'author': p.author, 'author_id': p.author_id,
        'date': time.strftime('%Y-%m-%d', time.localtime(p.created_at)), 'category': p.category
    } for p in posts]
    
    admin = User.query.filter_by(username='admin').first()
    admin_status = admin.status if admin else 'Exploring'
    admin_bio = admin.bio if admin else 'Explorer | Content Creator | Lifelong Learner\nCreating digital footprints across the web.'
    
    return render_template('index.html', posts=posts_data, is_admin=current_user.is_authenticated and current_user.is_admin,
                          current_user_id=current_user.id if current_user.is_authenticated else None, page='index',
                          category_filter=category_filter, tag_filter=tag_filter, search=search_query,
                          admin_status=admin_status, admin_bio=admin_bio)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
        
        login_user(user, True if request.form.get('remember') else False)
        flash('Login successful!', 'success')
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')
        
        if len(username) < 3 or len(password) < 6 or password != confirm:
            flash('Invalid input. Username min 3 chars, password min 6 chars.', 'danger')
            return render_template('signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return render_template('signup.html')
        
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.username != 'admin':
        flash('Admin only', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if request.form.get('status'):
            current_user.status = request.form.get('status')
        if request.form.get('bio'):
            current_user.bio = request.form.get('bio')
        current_user.theme_enabled = bool(request.form.get('theme_enabled'))
        db.session.commit()
        flash('Settings saved!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', page='settings')

@app.route('/tags')
def tags():
    return render_template('tags.html', tags=get_all_tags(), page='tags')

@app.route('/manage_tag', methods=['POST'])
@login_required
def manage_tag():
    if current_user.username != 'admin':
        flash('Admin only', 'danger')
        return redirect(url_for('tags'))
    
    tag_name = request.form.get('tag_name', '').strip()
    action = request.form.get('action', '')
    
    if action == 'add':
        if tag_name:
            existing = Tag.query.filter_by(name=tag_name).first()
            if not existing:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.commit()
                flash(f'Tag "{tag_name}" added', 'success')
            else:
                flash('Tag already exists', 'warning')
    elif action == 'delete':
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            db.session.delete(tag)
            db.session.commit()
            flash(f'Tag "{tag_name}" deleted', 'success')
    
    return redirect(url_for('tags'))

@app.route('/categories')
def categories():
    return render_template('categories.html', categories=get_all_categories(), page='categories')

@app.route('/archives')
def archives():
    return render_template('archives.html', archives=get_archives(), page='archives')

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', '随笔')
        tag_names = request.form.get('tags', '').strip()
        
        if not title or not content:
            flash('Title and content required', 'danger')
            return render_template('new_post.html')
        
        post = Post(title=title, content=content, summary=content[:100]+'...' if len(content)>100 else content,
                     author=current_user.username, author_id=current_user.id, category=category)
        db.session.add(post)
        db.session.flush()
        
        if tag_names:
            tag_list = [t.strip() for t in tag_names.split(',') if t.strip()]
            for tag_name in tag_list:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.session.add(tag)
                    db.session.flush()
                post.tags.append(tag)
        
        db.session.commit()
        flash('Post created!', 'success')
        return redirect(url_for('index'))
    
    all_tags = Tag.query.all()
    return render_template('new_post.html', page='new_post', all_tags=all_tags)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    comments_data = [{'id': c.id, 'author': c.author, 'content': c.content,
                      'created_at': time.strftime('%Y-%m-%d', time.localtime(c.created_at)), 'post_id': c.post_id} for c in comments]
    return render_template('post_detail.html', post=post, post_date=time.strftime('%Y-%m-%d', time.localtime(post.created_at)),
                          comments=comments_data, is_admin=current_user.is_authenticated and current_user.is_admin,
                          current_user_id=current_user.id if current_user.is_authenticated else None, page='post')

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    content = request.form.get('content', '').strip()
    if not content:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))
    
    author = current_user.username if current_user.is_authenticated else (request.form.get('author', '匿名').strip() or '匿名')
    author_id = current_user.id if current_user.is_authenticated else None
    comment = Comment(post_id=post_id, author=author, author_id=author_id, content=content)
    db.session.add(comment)
    db.session.commit()
    flash('Comment posted!', 'success')
    return redirect(url_for('post_detail', post_id=post_id))

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_admin and post.author_id != current_user.id:
        flash('No permission', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted', 'success')
    return redirect(url_for('index'))

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_admin and post.author_id != current_user.id:
        flash('No permission', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.category = request.form.get('category', '随笔')
        post.summary = post.content[:100]+'...' if len(post.content)>100 else post.content
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('post_detail', post_id=post_id))
    return render_template('edit_post.html', post=post)

@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    if not current_user.is_admin:
        flash('No permission', 'danger')
        return redirect(url_for('index'))
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted', 'success')
    return redirect(url_for('post_detail', post_id=post_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
