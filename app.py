
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Vianda, Cliente, Pedido, MovimientoDinero
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_key_123'
app.config['SQLALCHEMY_DATABASE_DATABASE_URI'] = 'sqlite:///comercio.db'

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Lógica simplificada para ejemplo
        user = Usuario.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/viandas')
@login_required
def viandas():
    lista = Vianda.query.all()
    return render_template('viandas.html', viandas=lista)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crear admin por defecto si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', password='admin_password')
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
