
import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'comercio_prod_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Vianda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Float)
    tipo = db.Column(db.String(20), default='diaria') # diaria, semanal, mensual
    ultima_facturacion = db.Column(db.DateTime, default=datetime.now)

class MovimientoDinero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10)) # Ingreso / Egreso
    monto = db.Column(db.Float)
    categoria = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.now)

def procesar_recurrentes():
    hoy = datetime.now()
    viandas = Vianda.query.filter(Vianda.tipo != 'diaria').all()
    for v in viandas:
        dias = (hoy - v.ultima_facturacion).days
        if (v.tipo == 'semanal' and dias >= 7) or (v.tipo == 'mensual' and dias >= 30):
            nuevo = MovimientoDinero(tipo='Ingreso', monto=v.precio, categoria=f'Cobro {v.tipo.capitalize()}: {v.nombre}')
            v.ultima_facturacion = hoy
            db.session.add(nuevo)
    db.session.commit()

@app.route('/')
def index():
    procesar_recurrentes()
    hoy = datetime.now()
    inicio_sem = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)
    
    def q(t, f): return db.session.query(db.func.sum(MovimientoDinero.monto)).filter(MovimientoDinero.tipo==t, MovimientoDinero.fecha>=f).scalar() or 0
    
    ctx = {
        'v_dia': q('Ingreso', hoy.replace(hour=0, minute=0)),
        'v_sem': q('Ingreso', inicio_sem),
        'v_mes': q('Ingreso', inicio_mes),
        'g_dia': q('Egreso', hoy.replace(hour=0, minute=0)),
        'g_sem': q('Egreso', inicio_sem),
        'g_mes': q('Egreso', inicio_mes)
    }
    return render_template('dashboard.html', **ctx, balance=ctx['v_mes'] - ctx['g_mes'])

@app.route('/viandas', methods=['GET', 'POST'])
def viandas():
    if request.method == 'POST':
        nueva = Vianda(nombre=request.form.get('nombre'), precio=float(request.form.get('precio', 0)), tipo=request.form.get('tipo', 'diaria'))
        db.session.add(nueva)
        db.session.add(MovimientoDinero(tipo='Ingreso', monto=nueva.precio, categoria=f'Venta inicial: {nueva.nombre}'))
        db.session.commit()
        return redirect(url_for('viandas'))
    return render_template('viandas.html', viandas=Vianda.query.all())

@app.route('/salidas', methods=['GET', 'POST'])
def salidas():
    if request.method == 'POST':
        nuevo = MovimientoDinero(tipo='Egreso', categoria=request.form.get('categoria'), monto=float(request.form.get('monto', 0)))
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('salidas'))
    return render_template('salidas.html', egresos=MovimientoDinero.query.filter_by(tipo='Egreso').all())

if __name__ == "__main__":
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
