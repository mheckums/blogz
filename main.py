from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:homework@localhost:8889/build-a-blog'

app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['GET', 'POST'])
def blog():

    blogs = Blog.query.all()
    return render_template('blog.html', title='Blogsss', blogs=blogs)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():

    if request.method == 'POST':
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

        new_blogpost = Blog(blogname, blogtext)
        
        db.session.add(new_blogpost)
        db.session.commit()

        blog_id = new_blogpost.id
        current_blog = Blog.query.get(blog_id)
        return render_template('blogpost.html', title='Blog Post', blog=current_blog)

    return render_template('newpost.html', title='New Post')

@app.route('/blogpost', methods=['GET'])
def blogpost():
    blog_id = request.args.get('id')

    current_blog = Blog.query.get(blog_id)

    #redirect('/blogpost', title='Blog Post', blog = current_blog)
    return render_template('blogpost.html', title='Blog Post', blog=current_blog)



if __name__ == '__main__':
    app.run()