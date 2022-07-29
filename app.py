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
app.secret_key = 'Kin3101513'  # Привет, Костик! пока хз куда лучше деть этот ключ..

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
    try:
        new = session['new-user']
    except:
        new = 0 
    if new == 1:
        session['new-user'] = 0
        return render_template("login.html", new=new, warningCode="You have been registered succesfully!")
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Query database for username
        one = "RandomHashPlaceholder"
        user = request.form.get("username").lower()
        rows = db.execute("SELECT * FROM users WHERE username = ?", (user,))
        for row in rows:
            uid = row[0]  # ID
            one = row[2]  # hash
        # Ensure username exists and password is correct  
        passw = request.form.get("password")
        if not check_password_hash(one, passw):
            return render_template("login.html", warningCode="Wrong name or password")
        # Remember which user has logged in
        session["user_id"] = uid
        return redirect("/")
    # GET
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("username").lower()
        names = db.execute("SELECT username FROM users WHERE username = ?", (name,))  # check db for username
        data = names.fetchone()
        if data != None:
            return render_template("/register.html", warningCode="User already exists")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if password != confirmation:
            return render_template("/register.html", warningCode="Wrong confirmation")
        hash1 = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)  # creates a password hash (encription)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (name,hash1,))
        db.commit()
        session["new-user"] = 1
        return redirect("/login")
    else:
        return render_template("/register.html")


@app.route("/", methods=["GET", "POST"]) 
@login_required
def index():
    user_id = session.get("user_id")
    names = db.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    name = names.fetchone()[0]  # user name
    if request.method == 'POST':  # languages are choosen 
        l1 = request.form['options1']
        l2 = request.form['options2']  # get value from radio buttons
        l3 = request.form['options3']
        session['l1'] = l1  
        session['l2'] = l2  # a way to send info via session !
        session['l3'] = l3
        if l1 == l2 or l1 == l3 or l2 == l3:
            return render_template("index.html", name=name, your="DIFFERENT")
        if request.form.get('translate') == 'translate': 
            return redirect('/trilingua')
        if request.form.get('test') == 'test': 
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
    name = names.fetchone()[0]  # user name
    if request.method == 'POST':
        if request.form.get('btn') == 'clear': 
            db.execute("DELETE FROM words WHERE user_id = ?", (user_id,))
            db.commit()
            return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, name=name)
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
                    return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, name=name, words=words, warningCode="No input detected")
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
        check = db.execute("SELECT translation FROM %s WHERE Word = ?" % (dict1), (inp,))
        row = check.fetchone()  # Check for empty cursor
        if row == None:
            wordsAll = db.execute("SELECT * FROM words WHERE user_id = ?", (user_id,))
            for i in wordsAll:
                words.append(i)  
            return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, name=name, words=words, warningCode="No such word")
        check = db.execute("SELECT translation FROM %s WHERE Word = ?" % (dict2), (inp,))
        row = check.fetchone()  # Check for empty cursor
        if row == None:
            wordsAll = db.execute("SELECT * FROM words WHERE user_id = ?", (user_id,))
            for i in wordsAll:
                words.append(i)  
            return render_template("trilingua.html", l1=l1, l2=l2, l3=l3, name=name, words=words, warningCode="No such word")
        # get translations
        word11 = db.execute("SELECT translation FROM %s WHERE Word = ?" % (dict1), (inp,))
        word1 = word11.fetchone()[0]
        word22 = db.execute("SELECT translation FROM %s WHERE Word = ?" % (dict2), (inp,))
        word2 = word22.fetchone()[0]
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
    name = names.fetchone()[0]
    l1 = session['l1']
    l2 = session['l2']  # get values from session
    l3 = session['l3']
    methods = ['Random', 'Personal', 'Category']
    types, left, middle, right = [], [], [], []
    # list all types in dict:
    type1 = db.execute("SELECT DISTINCT type FROM engrus ORDER BY type")
    for i in type1:
        types.append(i[0])

    if request.method == 'POST':
        # get lines number
        number = int(request.form.get('lines'))
        # set lang order
        dict1 = l1 + l2
        dict2 = l1 + l3
        # choose Test method
        if request.form.get('method') == 'Random':
            # -=RANDOM=- :
            for j in range(number):
                    # select random word
                le1 = db.execute("SELECT word FROM %s ORDER BY RANDOM()" % (dict1))
                le = le1.fetchone()[0]
                    # find translations
                mid1 = db.execute("SELECT translation FROM %s WHERE word = ?" % (dict1), (le,))
                mid = mid1.fetchone()[0]
                ri1 = db.execute("SELECT translation FROM %s WHERE word = ?" % (dict2), (le,))
                ri = ri1.fetchone()[0]
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
                return render_template("test.html", name=name, methods=methods, types=types, warningCode="No words in personal dictionary")
            
            for j in range(number):
                    # select random word from personal dict
                le1 = db.execute("SELECT word1 FROM words WHERE user_id = ? ORDER BY RANDOM()", (user_id,))
                le = le1.fetchone()[0]
                    # ..and it's translations
                mid1 = db.execute("SELECT word2 FROM words WHERE word1 = ?", (le,))
                mid = mid1.fetchone()[0]
                ri1 = db.execute("SELECT word3 FROM words WHERE word1 = ?", (le,))
                ri = ri1.fetchone()[0]
                # add to lists
                left.append(le)
                middle.append(mid)
                right.append(ri)

        elif request.form.get('method') == 'Category':
            # TYPES:
            type0 = request.form.get('type')  # selected type
            if not type0:
                return render_template("test.html", name=name, methods=methods, types=types, warningCode="Please choose category")
            for j in range(number):
                    # select random word with selected type
                le1 = db.execute("SELECT word FROM %s WHERE type = ? ORDER BY RANDOM()" % (dict1), (type0,))
                le = le1.fetchone()[0]
                    # find translations
                mid1 = db.execute("SELECT translation FROM %s WHERE word = ?" % (dict1), (le,))
                mid = mid1.fetchone()[0]
                ri1 = db.execute("SELECT translation FROM %s WHERE word = ?" % (dict2), (le,))
                ri = ri1.fetchone()[0]
                    # add to lists
                left.append(le)
                middle.append(mid)
                right.append(ri)
        return render_template("test.html", name=name, left=left, middle=middle, right=right, methods=methods, types=types)
    else:  # GET
        return render_template("test.html", name=name, methods=methods, types=types)


@app.route("/logout")
def logout():
    # Forget any user_ida
    session.clear()
    # Redirect user to login form
    return redirect("/")