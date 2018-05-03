from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '7h1sh@sb33n7h3h@rd3s7p@r7'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100),unique=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    username = db.Column(db.String(100))   
    password = db.Column(db.String(100))
    '''branch = db.Column(db.String(100))
    entrydate = db.Column(db.Integer)    
    exitdate = db.Column(db.Integer)
    base = db.Column(db.String(100))
    matches = db.Column(db.String(100))
    connections = db.Column(db.String(100))
    phone = db.Column(db.Integer)
    facebook = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    userimage = db.Column(db.String(100))'''


    def __init__(self, email, password, username, firstname, lastname):
        self.email = email
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        '''self.branch = branch
        self.entrydate = entrydate        
        self.exitdate = exitdate
        self.base = base
        self.matches = matches
        self.connections = connections
        self.phone = phone
        self.facebook = facebook
        self.linkedin = linkedin
        self.userimage = userimage'''

        

@app.before_request
def require_login():
    allowed_routes = ['login', 'register','index', 'blogs']
    if request.endpoint not in allowed_routes and 'email' not in session:
        flash("You must log in!")
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User/password incorrect or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    error = False
    email = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        '''phone = request.form['phone']
        linkedin = request.form['linkedin']
        facebook = request.form['facebook']
        branch = request.form['branch']
        entrydate = request.form['entrydate']        
        exitdate = request.form['exitdate']
        base = request.form['base']
        userimage = request.form['userimage']'''

        
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:            
            flash("User already exists")
        if not existing_user:
            if len(username) < 6 or len(username) > 20 or " " in username or username == "":
                error = True
                flash("Your entry must be between 6 and 20 characters and contain no spaces. Required field.")
            if len(password) < 6 or len(password) > 20 or " " in password or password == "":
                error = True
                flash("Your entry must be between 6 and 20 characters and contain no spaces. Required field.")
            if len(verify) < 6 or len(verify) > 20 or " " in verify or verify == "":
                error = True
                flash("Your entry must be between 6 and 20 characters and contain no spaces. Required field.")
            if " " in email or email == "":
                error = True
                flash("Your entry should contain no spaces. Required field.")

            if  lastname == "" or firstname == "":
                error = True
                flash("Required field.")
            '''if " " in phone or phone == "":
                error = True
                flash("Your entry should contain no spaces. Required field.")
            if " " in branch or branch == "":
                error = True
                flash("Your entry should contain no spaces. Required field.")
            if entrydate == "" or exitdate =="" or base == "":
                error = True
                flash("Your entry should contain no spaces. Required field.")'''
    
            if "." not in email: 
                error = True
                flash("Not a valid email. Must contain a ''.'' ")
            
            if "@" not in email:
                error = True
                flash("Not a valid email. Must contain a '@' ")

            if password != verify:
                error = True
                flash("Password and Verify Password fields must match.")

            

            if not error:
                new_user = User(email, password, username, firstname, lastname)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/blogs')
                
        return redirect('/register')

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')

@app.route('/blogs')
def blogs():   
    blogid = request.args.get('id')
    ownerid = request.args.get('owner_id')
    if ownerid:
        blogs = Blog.query.filter_by(ownerid=ownerid).all()
        return render_template('blogs.html', title="Blogs", blogs=blogs)
    if blogid:
        blogid = int(blogid)
        blogs = Blog.query.get(blogid)
        return render_template('blogs.html', blogs=blogs)
    blogs = Blog.query.all()
    return render_template('blogs.html',title="Blogs", 
        blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(email=session['email']).first()
    name = ""
    body = ""
    if request.method == 'POST':
        name = request.form['name']
        body = request.form['body']
        error = False
        if not name:
            flash("Blog must have a Title!", 'error')
            error = True
        if not body:
            flash("Blog must have a Body!", 'error')
            error = True
        if not error:
            blog = Blog(name,body,owner)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blogs?id={0}'.format(blog.id))
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('newpost.html',title="New Post", 
        blogs=blogs)

if __name__ == '__main__':
    app.run()