import sqlite3
from flask import Flask, request, redirect, render_template
from flask import session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Configure application
app = Flask(__name__)
app.secret_key = 'Kin3101513'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = sqlite3.connect('users.db', check_same_thread=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id

    session.clear()
    username = "Username"
    password = "Password"
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if request.form.get('register') == 'register':
            return redirect("/register")
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", username="Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", username="must provide password")

        # Query database for username
        one = "trijsdkj3"
        user = request.form.get("username").lower()
        rows = db.execute("SELECT * FROM users WHERE username = ?", (user,))
        for row in rows:
            uid = row[0]  # ID
            one = row[2]  # hash

        # Ensure username exists and password is correct  
        passw = request.form.get("password")
        if rows == []or not check_password_hash(one, passw):
            return render_template("login.html", username="Invalid username", password="or password")

        # Remember which user has logged in
        session["user_id"] = uid

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html", username=username, password=password)


@app.route("/register", methods=["GET", "POST"])
def register():
    username = "Username"
    password = "Password"
    confirm = "Confirm password"
    if request.method == "POST":
        if request.form.get('login') == 'login':
            return redirect("/login")
        name = request.form.get("username").lower()
        if not name:
            return render_template("/register.html", username = "Username", password = "needed", confirm = "!!!")
        names = db.execute("SELECT username FROM users WHERE username = ?", (name,))  # check db for username
        for row in names:
            if name == row[0]:  # check if name is already in DB
                return render_template("/register.html", username = "User", password = "already", confirm = "exists")

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password or not confirmation:
            return render_template("/register.html", username = "Enter", password = "password and", confirm = "confirmation")
        if password != confirmation:
            return render_template("/register.html", username = "!!!", password = "Wrong", confirm = "confirmation !!!")
        hash1 = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)  # creates a password hash (encription)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (name,hash1,))
        db.commit()
        return redirect("/")
    else:
        return render_template("/register.html", username=username, password=password, confirm=confirm)


@app.route("/", methods=["GET", "POST"]) 
@login_required
def index():
    user_id = session.get("user_id")
    names = db.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    for row in names:
        name = row[0] # user name

    if request.method == 'POST':  # languages are choosen 
        l1 = request.form['options1']
        l2 = request.form['options2']  # get value from radio buttons
        l3 = request.form['options3']
        session['l1'] = l1  
        session['l2'] = l2  # a way to send info via session !
        session['l3'] = l3

        if l1 == l2 or l1 == l3 or l2 == l3:
            return render_template("index.html", name=name, your="DIFFERENT")
        if request.form.get('btn0') == 'TL': 
            return redirect('/trilingua')
        if request.form.get('btn1') == 'test': 
            return redirect('/test')
    else:
        return render_template("index.html", name=name, your="your")


@app.route("/trilingua", methods=["GET", "POST"])
@login_required
def trilingua():
    l1 = session['l1']
    l2 = session['l2']  # get values from session
    l3 = session['l3']
    words=[]

    user_id = session.get("user_id")
    names = db.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    for row in names:
        name = row[0]

    if request.method == 'POST':

        if request.form.get('btn') == 'clear': 
            db.execute("DELETE FROM words WHERE user_id = ?", (user_id,))
            db.commit()
            return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, name=name)

        if request.form.get('btnTest') == 'test':
            return redirect('/test')

        if request.form.get('btnInd') == 'ind':
            return redirect('/')

        left, middle, right = 100, 200, 300  # rand values for forms
        # determine which form was filled
        if not request.form.get("left"):
            if not request.form.get("middle"):
                inp = request.form.get("right").lower()
                right = inp
                
                if not request.form.get("right"):
                    wordsAll = db.execute("SELECT * FROM words WHERE user_id = ?", (user_id,))
                    for i in wordsAll:
                        words.append(i)
                    return render_template("trilingua.html", l1="NO", l2="INPUT", l3="DETECTED", name=name, words=words)
            else: 
                inp = request.form.get("middle").lower()
                middle = inp
        else:
            inp = request.form.get("left").lower()
            left = inp

        # choose dicts:
        if left == inp:
            dict1 = l1 + l2
            dict2 = l1 + l3
        elif middle == inp:
            dict1 = l2 + l1
            dict2 = l2 + l3
        else:
            dict1 = l3 + l1
            dict2 = l3 + l2 

        # check input word
        db1 = sqlite3.connect("Dicts/" + dict1 + ".db", check_same_thread=False)
        db2 = sqlite3.connect("Dicts/" + dict2 + ".db", check_same_thread=False)
        
        check = db1.execute("SELECT translation FROM %s WHERE Word = ?" % (dict1), (inp,))
        row = check.fetchone()  # Check for empty cursor
        if row == None:
            db1.close()
            db2.close()
            wordsAll = db.execute("SELECT * FROM words WHERE user_id = ?", (user_id,))
            for i in wordsAll:
                words.append(i)  
            return render_template("trilingua.html", l1="no", l2="such", l3="word", name=name, words=words)
        
        check = db2.execute("SELECT translation FROM %s WHERE Word = ?" % (dict2), (inp,))
        row = check.fetchone()  # Check for empty cursor [2]
        if row == None:
            left, middle, right = 'No', 'such', 'word' 
            db1.close()
            db2.close()   
            return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, middle=middle, left=left, right=right)

        # get translations
        word11 = db1.execute("SELECT translation FROM %s WHERE Word = ?" % (dict1), (inp,))
        for row in word11:
            word1 = row[0]
        word22 = db2.execute("SELECT translation FROM %s WHERE Word = ?" % (dict2), (inp,))
        for row in word22:
            word2 = row[0]

        # output translations
        if left == inp:
            middle = word1
            right = word2
        elif middle == inp:
            left = word1
            right = word2
        else:
            left = word1
            middle = word2 

        # insert translations to DB:
        check = db.execute("SELECT word1 FROM words WHERE user_id = ? AND word1 = ? AND word2 = ? AND word3 = ?", (user_id, left, middle, right,))
        row = check.fetchone()  # Check for empty cursor
        if row == None:
            db.execute("INSERT INTO words(user_id, word1, word2, word3) VALUES (?, ?, ?, ?)", (user_id, left, middle, right,))
            db.commit()

        wordsAll = db.execute("SELECT * FROM words WHERE user_id = ?", (user_id,))
        for i in wordsAll:
            words.append(i)
        
        db1.close()
        db2.close()
        return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, middle=middle, left=left, right=right, words=words, name=name)
    else:
        wordsAll = db.execute("SELECT * FROM words WHERE user_id = ?", (user_id,))
        for i in wordsAll:
            words.append(i)
        return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, words=words, name=name)


@app.route("/test", methods=["GET", "POST"])  
@login_required     
def test():
    user_id = session.get("user_id")
    names = db.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    for row in names:
        name = row[0]

    l1 = session['l1']
    l2 = session['l2']  # get values from session
    l3 = session['l3']
    methods = ['Random', 'Personal', 'Category']
    types, left, middle, right = [], [], [], []
    # list all types in dict:
    type1 = sqlite3.connect("Dicts/engrus.db").execute("SELECT DISTINCT type FROM engrus ORDER BY type")
    for i in type1:
        types.append(i[0])

    if request.method == 'POST':
        # get lines number
        number = int(request.form.get('lines'))
        # set lang order
        dict1 = l1 + l2
        dict2 = l1 + l3
        # connect to needed dicts
        db1 = sqlite3.connect("Dicts/" + dict1 + ".db", check_same_thread=False)
        db2 = sqlite3.connect("Dicts/" + dict2 + ".db", check_same_thread=False)
            
        # choose Test method  
        if request.form.get('method') == 'Random':
            # -=RANDOM=- :
            for j in range(number):
                    # select random word
                le1 = db1.execute("SELECT word FROM %s ORDER BY RANDOM()" % (dict1))
                for row in le1:
                    le = row[0]
                    # find translations
                mid1 = db1.execute("SELECT translation FROM %s WHERE word = ?" % (dict1), (le,))
                for row in mid1:
                    mid = row[0]
                ri1 = db2.execute("SELECT translation FROM %s WHERE word = ?" % (dict2), (le,))
                for row in ri1:
                    ri = row[0]
                    # add to lists
                left.append(le)
                middle.append(mid)
                right.append(ri)

        elif request.form.get('method') == 'Personal':
            # -=PERSONAL=- :
            # check for words in personal dicts
            check = db.execute("SELECT word1 FROM words WHERE user_id = ?", (user_id,))
            row = check.fetchone()  # Check for empty cursor
            if row == None:
                db1.close()
                db2.close()
                return render_template("test.html", l1=l1, l2=l2, l3=l3, name=name, left=["No words"], middle=["in personal"], right=["dictionary :("], methods=methods, types=types)
            
            for j in range(number):
                    # select random word from personal dict
                le1 = db.execute("SELECT word1 FROM words WHERE user_id = ? ORDER BY RANDOM()", (user_id,))
                for j in le1:
                    le = j[0]
                    # ..and it's translations
                mid1 = db.execute("SELECT word2 FROM words WHERE word1 = ?", (le,))
                for j in mid1:
                    mid = j[0]
                ri1 = db.execute("SELECT word3 FROM words WHERE word1 = ?", (le,))
                for j in ri1:
                    ri = j[0]
                # add to lists
                left.append(le)
                middle.append(mid)
                right.append(ri)

        elif request.form.get('method') == 'Category':
            # TYPES:
            type0 = request.form.get('type')  # selected type
            for j in range(number):
                    # select random word with selected type
                le1 = db1.execute("SELECT word FROM %s WHERE type = ? ORDER BY RANDOM()" % (dict1), (type0,))
                for j in le1:
                    le = j[0]    
                    # find translations
                mid1 = db1.execute("SELECT translation FROM %s WHERE word = ?" % (dict1), (le,))
                for j in mid1:
                    mid = j[0]
                ri1 = db2.execute("SELECT translation FROM %s WHERE word = ?" % (dict2), (le,))
                for j in ri1:
                    ri = j[0]
                    # add to lists
                left.append(le)
                middle.append(mid)
                right.append(ri)

        db1.close()
        db2.close()
        return render_template("test.html", l1=l1, l2=l2, l3=l3, name=name, left=left, middle=middle, right=right, methods=methods, types=types)
    else:  # GET
        return render_template("test.html", l1=l1, l2=l2, l3=l3, name=name, methods=methods, types=types)


@app.route("/logout")
def logout():

    # Forget any user_ida
    session.clear()

    # Redirect user to login form
    return redirect("/")


if __name__ == "__main__":  # to start the app
    app.run(debug=True)
