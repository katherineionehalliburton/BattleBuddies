from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://battlebuddies:battlebuddies@localhost:8889/battlebuddies'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '7h1sh@sb33n7h3h@rd3s7p@r7'
        

class User(db.Model):

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
    password = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)     


    def __init__(self, password, username, firstname, lastname, email, phone, facebook, linkedin, userimage, branch, base, entrydate, exitdate):
        self.username = username
        self.password = password
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


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'matches']
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
            flash("Logged in")
            return redirect('/matches')
        else:
            flash('User/password incorrect or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    error = False
    username = ''
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
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
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
                new_user = User(password,username,firstname,lastname,email,phone,facebook,linkedin,userimage,branch,base,entrydate,exitdate)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return render_template('matches.html')
                
        return redirect('/register')

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/matches')
def matches():   
    usermatchbranches = User.query.with_entities(User.branch, db.func.count()).group_by(User.branch).having(db.func.count() > 1).all()
    usermatchbases = User.query.with_entities(User.base, db.func.count()).group_by(User.base).having(db.func.count() > 1).all()
    
    print (usermatchbranches)


if __name__ == '__main__':
    app.run()