from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:homework@localhost:8889/blogz'

app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    blogs = db.relationship('Blog', backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
def index():
    users = User.query.all()
    
    return render_template('index.html', users=users)

@app.route('/blog', methods=['GET', 'POST'])
def blog():

    if request.args.get("id"):
        blog_id = request.args.get("id")
        blogs = Blog.query.filter_by(blog_id)
        return render_template('userpost.html', title='Blogsss', blogs=blogs)
    elif request.args.get("user"):
        user_id = request.args.get("user")
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('userpost.html', title="Blogsss", blogs=blogs)
    else:

        blogs = Blog.query.all()
        return render_template('blog.html', title='Blogsss', blogs=blogs)

@app.route('/userpost', methods=['GET', 'POST'])
def userpost():

    user_id = request.args.get("user")
    user_posts = Blog.query.filter_by(owner_id=user_id).all()

    return render_template('userpost.html', title="Blogsss", blogs=user_posts)



@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    if request.method == 'POST':

        owner = User.query.filter_by(username = session['username']).first()
        blogname = request.form['blogtitle']
        blogtext = request.form['blogtext']
        
        name_error = ''
        text_error = ''

        if blogname == '':
            name_error = 'Please title this blogpost'
            return render_template('newpost.html', title='New Post', blogtext=blogtext, name_error=name_error)

        if blogtext == '':
            text_error = 'Please add blog text'
            return render_template('newpost.html', title='New Post', blogname=blogname, text_error=text_error)

        new_blogpost = Blog(blogname, blogtext, owner)
        
        db.session.add(new_blogpost)
        db.session.commit()

        blog_id = new_blogpost.id
        current_blog = Blog.query.get(blog_id)
        return render_template('blogpost.html', title='Blog Post', blog=current_blog)

    return render_template('newpost.html', title='New Post')

@app.route('/blogpost', methods=['GET'])
def blogpost():


    blog_id = request.args.get('id')

    user_id = request.args.get('user')

    
    if blog_id:
        current_blog = Blog.query.get(blog_id)
        return render_template('blogpost.html', title='Blog Post', blog=current_blog)

    if user_id:
        current_blog = User.query.filter_by(id=user_id).all()
        return render_template("userpost.html", blog=current_blog)

    # redirect('/blogpost', title='Blog Post', blog =current_blog)
    # return render_template('blogpost.html', title='Blog Post', blog=current_blog)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        #user = User.query.filter_by(email=email).first()
        typed_user = request.form['username']
        user = User.query.filter_by(username=typed_user).first()
        

        password_error = ''
        username_error = ''
        #if database_user and user.password == password:
        #    session['email'] = email
        #    flash("Logged in")
        #    return redirect('/')
        if user and user.password == password:
            session['username'] = typed_user
            return redirect('/newpost')

        if user and user.password != password:
            password_error = 'Password is invalid'
            return render_template('login.html', password_error=password_error)

        if not typed_user:
            username_error = 'Username is not registered'
            return render_template('login.html', username_error=username_error)


    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verifypassword']

        # TODO - validate user's data
        username_error = ''
        password_error = ''
        verify_password_error = ''


        if not username:
            username_error = 'Please enter a username'
            return render_template('signup.html', username_error=username_error)
        if not password:
            password_error = 'Please enter a password'
            return render_template('signup.html', username=username, password_error=password_error)
        if not verify:
            verify_password_error = 'Please verify the password'
            return render_template('signup.html', username=username, verify_password_error=verify_password_error)

        if password != verify:
            verify_password_error = 'Password and Verify Password do not match'
            return render_template('signup.html', username=username, verify_password_error=verify_password_error)

        if len(username) < 3:
            username_error = 'Username is invalid number of characters (less than 3)'
            return render_template('signup.html',  username=username, username_error=username_error)


        if len(password) < 3:
            password_error = 'Password is invalid number of characters (less than 3)'
            return render_template('signup.html',  username=username, password_error=password_error)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            username_error = 'Username already exists'
            return render_template('signup.html', username_error=username_error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')



if __name__ == '__main__':
    app.run()