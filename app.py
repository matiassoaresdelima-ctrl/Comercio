
import os
from datetime import datetime
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

class MovimientoDinero(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10))
    monto = db.Column(db.Float)
    categoria = db.Column(db.String(50))
    fecha = db.Column(db.DateTime, default=datetime.now)

@app.route('/')
def index():
    try:
        ventas = db.session.query(db.func.sum(Vianda.precio)).scalar() or 0.0
        gastos = db.session.query(db.func.sum(MovimientoDinero.monto)).filter(MovimientoDinero.tipo == 'Egreso').scalar() or 0.0
        return render_template('dashboard.html', total_ventas=ventas, total_gastos=gastos, balance=ventas-gastos)
    except:
        return render_template('dashboard.html', total_ventas=0, total_gastos=0, balance=0)

@app.route('/viandas', methods=['GET', 'POST'])
def viandas():
    if request.method == 'POST':
        nueva = Vianda(nombre=request.form.get('nombre'), precio=float(request.form.get('precio', 0)))
        db.session.add(nueva)
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

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
