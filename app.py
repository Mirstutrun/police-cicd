from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///police.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= МОДЕЛИ БАЗЫ ДАННЫХ (5 таблиц) =================

class Officer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rank = db.Column(db.String(50), nullable=False)
    badge_number = db.Column(db.String(20), unique=True, nullable=False)
    cases = db.relationship('Case', backref='officer', lazy=True)

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Открыто')
    officer_id = db.Column(db.Integer, db.ForeignKey('officer.id'), nullable=False)
    evidence = db.relationship('Evidence', backref='case', lazy=True)
    interrogations = db.relationship('Interrogation', backref='case', lazy=True)

class Suspect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    features = db.Column(db.Text, nullable=True)
    interrogations = db.relationship('Interrogation', backref='suspect', lazy=True)

class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)

class Interrogation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    suspect_id = db.Column(db.Integer, db.ForeignKey('suspect.id'), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)

with app.app_context():
    db.create_all()

# ================= ГЛАВНАЯ СТРАНИЦА =================

@app.route('/')
def index():
    return render_template('index.html')

# ================= 1. CRUD СОТРУДНИКОВ (Officers) =================
@app.route('/officers')
def officers():
    return render_template('officers.html', officers=Officer.query.all())

@app.route('/add_officer', methods=['GET', 'POST'])
def add_officer():
    if request.method == 'POST':
        new_officer = Officer(name=request.form['name'], rank=request.form['rank'], badge_number=request.form['badge_number'])
        db.session.add(new_officer)
        db.session.commit()
        return redirect('/officers')
    return render_template('add_officer.html')

@app.route('/update_officer/<int:id>', methods=['GET', 'POST'])
def update_officer(id):
    officer = Officer.query.get_or_404(id)
    if request.method == 'POST':
        officer.name = request.form['name']
        officer.rank = request.form['rank']
        officer.badge_number = request.form['badge_number']
        db.session.commit()
        return redirect('/officers')
    return render_template('update_officer.html', officer=officer)

@app.route('/delete_officer/<int:id>')
def delete_officer(id):
    db.session.delete(Officer.query.get_or_404(id))
    db.session.commit()
    return redirect('/officers')

# ================= 2. CRUD ДЕЛ (Cases) =================
@app.route('/cases')
def cases():
    return render_template('cases.html', cases=Case.query.all())

@app.route('/add_case', methods=['GET', 'POST'])
def add_case():
    if request.method == 'POST':
        new_case = Case(title=request.form['title'], status=request.form['status'], officer_id=request.form['officer_id'])
        db.session.add(new_case)
        db.session.commit()
        return redirect('/cases')
    return render_template('add_case.html', officers=Officer.query.all())

@app.route('/update_case/<int:id>', methods=['GET', 'POST'])
def update_case(id):
    case = Case.query.get_or_404(id)
    if request.method == 'POST':
        case.title = request.form['title']
        case.status = request.form['status']
        case.officer_id = request.form['officer_id']
        db.session.commit()
        return redirect('/cases')
    return render_template('update_case.html', case=case, officers=Officer.query.all())

@app.route('/delete_case/<int:id>')
def delete_case(id):
    db.session.delete(Case.query.get_or_404(id))
    db.session.commit()
    return redirect('/cases')

# ================= 3. CRUD ПОДОЗРЕВАЕМЫХ (Suspects) =================
@app.route('/suspects')
def suspects():
    return render_template('suspects.html', suspects=Suspect.query.all())

@app.route('/add_suspect', methods=['GET', 'POST'])
def add_suspect():
    if request.method == 'POST':
        new_suspect = Suspect(name=request.form['name'], age=request.form['age'], features=request.form['features'])
        db.session.add(new_suspect)
        db.session.commit()
        return redirect('/suspects')
    return render_template('add_suspect.html')

@app.route('/update_suspect/<int:id>', methods=['GET', 'POST'])
def update_suspect(id):
    suspect = Suspect.query.get_or_404(id)
    if request.method == 'POST':
        suspect.name = request.form['name']
        suspect.age = request.form['age']
        suspect.features = request.form['features']
        db.session.commit()
        return redirect('/suspects')
    return render_template('update_suspect.html', suspect=suspect)

@app.route('/delete_suspect/<int:id>')
def delete_suspect(id):
    db.session.delete(Suspect.query.get_or_404(id))
    db.session.commit()
    return redirect('/suspects')

# ================= 4. CRUD УЛИК (Evidence) =================
@app.route('/evidence')
def evidence():
    return render_template('evidence.html', evidences=Evidence.query.all())

@app.route('/add_evidence', methods=['GET', 'POST'])
def add_evidence():
    if request.method == 'POST':
        new_evidence = Evidence(item_name=request.form['item_name'], description=request.form['description'], case_id=request.form['case_id'])
        db.session.add(new_evidence)
        db.session.commit()
        return redirect('/evidence')
    return render_template('add_evidence.html', cases=Case.query.all())

@app.route('/update_evidence/<int:id>', methods=['GET', 'POST'])
def update_evidence(id):
    evidence = Evidence.query.get_or_404(id)
    if request.method == 'POST':
        evidence.item_name = request.form['item_name']
        evidence.description = request.form['description']
        evidence.case_id = request.form['case_id']
        db.session.commit()
        return redirect('/evidence')
    return render_template('update_evidence.html', evidence=evidence, cases=Case.query.all())

@app.route('/delete_evidence/<int:id>')
def delete_evidence(id):
    db.session.delete(Evidence.query.get_or_404(id))
    db.session.commit()
    return redirect('/evidence')

# ================= 5. CRUD ДОПРОСОВ (Interrogations) =================
@app.route('/interrogations')
def interrogations():
    return render_template('interrogations.html', interrogations=Interrogation.query.all())

@app.route('/add_interrogation', methods=['GET', 'POST'])
def add_interrogation():
    if request.method == 'POST':
        new_interrogation = Interrogation(date=request.form['date'], notes=request.form['notes'], suspect_id=request.form['suspect_id'], case_id=request.form['case_id'])
        db.session.add(new_interrogation)
        db.session.commit()
        return redirect('/interrogations')
    return render_template('add_interrogation.html', suspects=Suspect.query.all(), cases=Case.query.all())

@app.route('/update_interrogation/<int:id>', methods=['GET', 'POST'])
def update_interrogation(id):
    interrogation = Interrogation.query.get_or_404(id)
    if request.method == 'POST':
        interrogation.date = request.form['date']
        interrogation.notes = request.form['notes']
        interrogation.suspect_id = request.form['suspect_id']
        interrogation.case_id = request.form['case_id']
        db.session.commit()
        return redirect('/interrogations')
    return render_template('update_interrogation.html', interrogation=interrogation, suspects=Suspect.query.all(), cases=Case.query.all())

@app.route('/delete_interrogation/<int:id>')
def delete_interrogation(id):
    db.session.delete(Interrogation.query.get_or_404(id))
    db.session.commit()
    return redirect('/interrogations')

if __name__ == '__main__':
    app.run(debug=True)