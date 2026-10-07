from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'college_crm.db')
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-secret-key')


def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    c = db()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    c.execute('CREATE TABLE IF NOT EXISTS crm_state (user_id INTEGER PRIMARY KEY, data TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))')
    c.commit(); c.close()

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('college_crm.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        c=db(); u=c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone(); c.close()
        if u and check_password_hash(u['password'], password):
            session['user_id']=u['id']; session['user_name']=u['name']; session['user_email']=u['email']
            return redirect(url_for('home'))
        return render_template('login.html', error='Invalid email or password.')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        if len(name)<2 or '@' not in email or len(password)<6:
            return render_template('register.html', error='Enter valid details. Password must be at least 6 characters.')
        c=db()
        try:
            cur=c.execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(name,email,generate_password_hash(password)))
            c.execute('INSERT INTO crm_state(user_id,data) VALUES(?,?)',(cur.lastrowid,'{}'))
            c.commit(); uid=cur.lastrowid
        except sqlite3.IntegrityError:
            c.close(); return render_template('register.html', error='An account with this email already exists.')
        c.close(); session['user_id']=uid; session['user_name']=name; session['user_email']=email
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

@app.route('/api/state', methods=['GET','POST'])
def state():
    if 'user_id' not in session: return jsonify({'error':'unauthorized'}),401
    uid=session['user_id']; c=db()
    if request.method=='GET':
        row=c.execute('SELECT data FROM crm_state WHERE user_id=?',(uid,)).fetchone(); c.close()
        import json
        return jsonify({'data': json.loads(row['data']) if row else {}})
    payload=request.get_json(silent=True) or {}; data=payload.get('data')
    if not isinstance(data, dict): c.close(); return jsonify({'error':'invalid data'}),400
    import json
    text=json.dumps(data,separators=(',',':'))
    c.execute('INSERT INTO crm_state(user_id,data) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP',(uid,text))
    c.commit(); c.close(); return jsonify({'ok':True})

@app.context_processor
def inject_user():
    return {'user_name':session.get('user_name'), 'user_email':session.get('user_email')}

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
