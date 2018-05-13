from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://battlebuddies:battlebuddies@localhost:8889/battlebuddies'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '7h1sh@sb33n7h3h@rd3s7p@r7'

class Info(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.Integer)
    facebook = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    userimage = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    base = db.Column(db.String(100))
    entrydate = db.Column(db.Integer)
    exitdate = db.Column(db.Integer) 
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))  

    def __init__(self, firstname, lastname, email, phone, facebook, linkedin, userimage, branch, base, entrydate, exitdate, owner):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.phone = phone
        self.facebook = facebook
        self.linkedin = linkedin
        self.userimage = userimage
        self.branch = branch
        self.base = base
        self.entrydate = entrydate   
        self.exitdate = exitdate  
        self.owner = owner   

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)     
    info = db.relationship('Info', backref='owner')


    def __init__(self, password, username):
        self.username = username
        self.password = password
        


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'matches', 'profile']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("You must log in!")
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            ### - todo - run database query to check for new matches here
            flash("Logged in")
            return redirect('/matches')
        else:
            flash('User/password incorrect or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    error = False
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
                
        existing_user = User.query.filter_by(username=username).first()
        
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

            if password != verify:
                error = True
                flash("Password and Verify Password fields must match.")
            
            if not error:
                new_user = User(password,username)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return render_template('profile.html')
                
        return redirect('/register')

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/matches')
def matches():   
    
    return render_template('matches.html',title="Matches", 
        info=info)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    owner = User.query.filter_by(username=session['username']).first()
    email = ""
    firstname = ""
    lastname = ""
    phone = ""
    facebook = ""
    branch = ""
    base = ""
    linkedin = "" 
    entrydate = ""   
    exitdate = ""   
    userimage = ""
    if request.method == 'POST':
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        phone = request.form['phone']
        facebook = request.form['facebook']
        branch = request.form['branch']
        base = request.form['base']
        linkedin = request.form['linkedin'] 
        entrydate = request.form['entrydate']        
        exitdate = request.form['exitdate']     
        userimage = request.form['userimage']
        error = False
        if not email and not phone:
            flash("Profile must have an email or phone for contact!", 'error')
            error = True
        if not firstname:
            flash("First name required!", 'error')
            error = True
        if not lastname:
            flash("Last name required!", 'error')
            error = True
        if not branch:
            flash("Branch required!", 'error')
            error = True
        if not base:
            flash("Base Assignment required!", 'error')
            error = True
        if not entrydate:
            flash("Enlistment Date required!", 'error')
            error = True
        if not exitdate:
            flash("Exit Date required!", 'error')
            error = True
        if not userimage:
            flash("Service Image required!", 'error')
            error = True
        if " " in email or email == "":
            error = True
            flash("Your entry should contain no spaces. Required field.")
    
        if "." not in email: 
            error = True
            flash("Not a valid email. Must contain a ''.'' ")
            
        if "@" not in email:
            error = True
            flash("Not a valid email. Must contain a '@' ")

            
        if not error:
            info = Info(firstname,lastname,email,phone,facebook,linkedin,userimage,branch,base,entrydate,exitdate,owner)
            db.session.add(info)
            db.session.commit()
            return render_template('matches.html',title="Your Matches")

    info = Info.query.filter_by(owner=owner).all()
    return render_template('matches.html',title="Your Matches", 
        info=info)

if __name__ == '__main__':
    app.run()