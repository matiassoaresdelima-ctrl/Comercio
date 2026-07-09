
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime

# Importar modelos
from models import db, Usuario, Vianda, Cliente, Pedido, MovimientoDinero

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'prod_key_999')

# Configuración crítica para Render/PostgreSQL
uri = os.environ.get('DATABASE_URL', 'sqlite:///comercio.db')
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    hoy = datetime.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0)
    v_mes, g_mes, balance, conteo_ventas = MovimientoDinero.get_financial_summary(inicio_mes)
    cant_viandas = Vianda.get_total_viandas()
    
    stats = {
        'v_mes': v_mes, 'g_mes': g_mes, 'balance': balance,
        'cant_viandas': cant_viandas,
        'margen': round((balance / v_mes * 100) if v_mes > 0 else 0, 1),
        'ticket_promedio': round((v_mes / conteo_ventas) if conteo_ventas > 0 else 0, 2),
        'fecha_mes': inicio_mes.strftime('%d/%m/%Y')
    }
    return render_template('dashboard.html', **stats)

@app.route('/viandas', methods=['GET', 'POST'])
@login_required
def viandas():
    if request.method == 'POST':
        nueva = Vianda(nombre=request.form.get('nombre'), precio=float(request.form.get('precio', 0)), disponible=True)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for('viandas'))
    lista = Vianda.query.all()
    return render_template('viandas.html', viandas=lista)

@app.route('/salidas', methods=['GET', 'POST'])
@login_required
def salidas():
    if request.method == 'POST':
        monto = float(request.form.get('monto', 0))
        nuevo = MovimientoDinero(tipo='Egreso', categoria=request.form.get('categoria'), monto=monto)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('salidas'))
    egresos = MovimientoDinero.query.filter_by(tipo='Egreso').all()
    return render_template('salidas.html', egresos=egresos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('index'))
        flash('Error de acceso', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
