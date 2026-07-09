
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from models import db, Vianda, Cliente, Pedido, MovimientoDinero

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_fija_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    try:
        total_ventas = db.session.query(db.func.sum(Pedido.total)).scalar() or 0.0
        total_gastos = db.session.query(db.func.sum(MovimientoDinero.monto)).filter(MovimientoDinero.tipo == 'Egreso').scalar() or 0.0
        balance = total_ventas - total_gastos
        return render_template('dashboard.html', total_ventas=total_ventas, total_gastos=total_gastos, balance=balance)
    except:
        return render_template('dashboard.html', total_ventas=0, total_gastos=0, balance=0)

@app.route('/viandas', methods=['GET', 'POST'])
def viandas():
    if request.method == 'POST':
        nueva = Vianda(nombre=request.form.get('nombre'), precio=float(request.form.get('precio', 0)), disponible=True)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for('viandas'))
    lista = Vianda.query.all()
    return render_template('viandas.html', viandas=lista)

@app.route('/salidas', methods=['GET', 'POST'])
def salidas():
    if request.method == 'POST':
        nuevo = MovimientoDinero(tipo='Egreso', categoria=request.form.get('categoria'), monto=float(request.form.get('monto', 0)), fecha=datetime.now())
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('salidas'))
    egresos = MovimientoDinero.query.filter_by(tipo='Egreso').all()
    return render_template('salidas.html', egresos=egresos)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
