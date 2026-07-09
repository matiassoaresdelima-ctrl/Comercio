
import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Importar los modelos actualizados
from models import db, Usuario, Vianda, Cliente, Pedido, MovimientoDinero

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'comercio_prod_123')

# Configuración de Base de Datos
uri = os.environ.get('DATABASE_URL', 'sqlite:///comercio.db')
if uri.startswith("postgres://"):
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

    # Obtener resúmenes financieros y conteo de ventas usando el método del modelo
    v_mes, g_mes, balance, conteo_ventas = MovimientoDinero.get_financial_summary(inicio_mes)

    # Obtener el total de viandas usando el método del modelo
    cant_viandas = Vianda.get_total_viandas()

    # Calcular KPIs
    margen = (balance / v_mes * 100) if v_mes > 0 else 0
    ticket_promedio = (v_mes / conteo_ventas) if conteo_ventas > 0 else 0

    stats = {
        'v_mes': v_mes, 'g_mes': g_mes, 'balance': balance,
        'cant_viandas': cant_viandas, 'margen': round(margen, 1),
        'ticket_promedio': round(ticket_promedio, 2),
        'fecha_mes': inicio_mes.strftime('%d/%m/%Y')
    }
    return render_template('dashboard.html', **stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'): # WARNING: Clear text password for demo
            login_user(user)
            return redirect(url_for('index'))
        flash('Credenciales inválidas', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/salidas', methods=['GET', 'POST'])
@login_required
def salidas():
    if request.method == 'POST':
        monto = float(request.form.get('monto', 0))
        categoria = request.form.get('categoria')
        descripcion = request.form.get('descripcion', '')
        nuevo_gasto = MovimientoDinero(tipo='Egreso', categoria=categoria, monto=monto, descripcion=descripcion)
        db.session.add(nuevo_gasto)
        db.session.commit()
        flash('Gasto registrado exitosamente.', 'success')
        return redirect(url_for('salidas'))
    egresos = MovimientoDinero.query.filter_by(tipo='Egreso').order_by(MovimientoDinero.fecha.desc()).all()
    return render_template('salidas.html', egresos=egresos)

@app.route('/viandas', methods=['GET', 'POST'])
@login_required
def viandas():
    if request.method == 'POST':
        nueva = Vianda(
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            precio=float(request.form.get('precio', 0)),
            disponible=True
        )
        db.session.add(nueva)
        db.session.commit()
        flash('Vianda agregada exitosamente.', 'success')
        return redirect(url_for('viandas'))

    lista = Vianda.query.all()
    return render_template('viandas.html', viandas=lista)

@app.route('/eliminar_vianda/<int:id>')
@login_required
def eliminar_vianda(id):
    v = Vianda.query.get_or_404(id)
    db.session.delete(v)
    db.session.commit()
    flash('Vianda eliminada exitosamente.', 'success')
    return redirect(url_for('viandas'))

if __name__ == '__main__':
    # Detect if running within a Colab interactive cell vs. a separate script execution
    if 'IPython' in sys.modules and 'google.colab' in sys.modules:
        print("Flask app defined. To run it, execute '!python app.py' in a new cell.")
        # Ensure database is initialized even if not running the app
        with app.app_context():
            db.create_all()
            if not Usuario.query.filter_by(username='admin').first():
                admin = Usuario(username='admin', password='admin_password') # WARNING: Clear text password for demo
                db.session.add(admin)
                db.session.commit()
    else:
        port = int(os.environ.get('PORT', 5000))
        with app.app_context():
            db.create_all()
            # Crear admin por defecto si no existe
            if not Usuario.query.filter_by(username='admin').first():
                admin = Usuario(username='admin', password='admin_password') # WARNING: Clear text password for demo
                db.session.add(admin)
                db.session.commit()

        print(f"
Flask app starting on http://127.0.0.1:{port} and http://{os.environ.get('COLAB_JUPYTER_IP', '0.0.0.0')}:{port}")
        print("Accede a la aplicación usando una de estas URLs.
")
        app.run(host='0.0.0.0', port=port, debug=False)
