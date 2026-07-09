
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Usuario, Vianda, Cliente, Pedido, MovimientoDinero
import os
import logging

app = Flask(__name__)
# Usamos una clave fija para evitar que las sesiones expiren al reiniciar el servidor en Render
app.config['SECRET_KEY'] = 'CLAVE_ESTATICA_COMPARTIDA_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logging.basicConfig(level=logging.DEBUG)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        app.logger.debug(f'Intento de login para: {username}')
        
        user = Usuario.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user, remember=True)
            app.logger.debug('Login exitoso, redirigiendo...')
            return redirect(url_for('index'))
        else:
            app.logger.debug('Credenciales fallidas')
            flash('Usuario o contraseña incorrectos')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    with app.app_context():
        db.create_all()
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(username='admin', password='admin_password')
            db.session.add(admin)
            db.session.commit()
    app.run(host='0.0.0.0', port=port)
