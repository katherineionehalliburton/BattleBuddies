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
    friends = db.relationship('Friends', backref='owner')


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


class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    friends = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, friends, owner):
        self.friends = friends
        self.owner = owner



@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'friends']
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
            flash("User already exists", 'error')
        if not existing_user:
            if len(username) < 6 or len(username) > 12 or " " in username or username == "":
                error = True
                flash("Your Username must be between 6 and 12 characters and contain no spaces. Required field.", 'error')
            if len(password) < 8 or len(password) > 15 or " " in password or password == "":
                error = True
                flash("Your Password must be between 8 and 15 characters and contain no spaces. Required field.", 'error')

            if password != verify:
                error = True
                flash("Password and Verify Password fields must match.", 'error')

            if not email and not phone:
                flash("Profile must have an email OR phone for contact. WE WILL NEVER SELL YOUR INFORMATION! We will only ever contact you by email, and only at your request!", 'error')
                error = True

            if " " in email:
                error = True
                flash("Your Email should contain no spaces. Required field.", 'error')
                
            if "@" not in email or "." not in email:
                error = True
                flash("Not a valid email. Must contain a '@' ", 'error')

            if not firstname or not lastname or not branch or not base or not entrydate or not exitdate:
                flash("All fields with an '*' are required!", 'error')
                error = True            
            
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

@app.route('/matches', methods=['POST', 'GET'])
def matches():   
    user_id = request.args.get('id')
    if user_id:
        user_id = int(user_id)
        users = User.query.get(user_id)
        users = User.query.filter_by(user_id=user_id).all()
        return render_template('matches.html', title="Matches", users=users)
    users = User.query.all()
    return render_template('matches.html',title="Matches", 
        users=users)
    
'''
    usermatchbases = User.query.with_entities(User.base, db.func.count()).group_by(User.base).having(db.func.count() > 1).all()
        if usermatchbases:
            return render_template('matches.html', title='Matches', usermatchbases=usermatchbases)'''
        

@app.route('/friends', methods=['POST', 'GET'])
def friends():
    return render_template('friends.html')


if __name__ == '__main__':
    app.run()