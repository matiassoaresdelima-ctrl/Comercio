
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Vianda, Cliente, Pedido, MovimientoDinero
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'comercio_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    # Datos básicos para el dashboard
    total_ventas = db.session.query(db.func.sum(Pedido.total)).scalar() or 0.0
    conteo_pedidos = Pedido.query.count()
    return render_template('dashboard.html', total_ventas=total_ventas, conteo_pedidos=conteo_pedidos)

@app.route('/viandas', methods=['GET', 'POST'])
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
        return redirect(url_for('viandas'))
    
    lista = Vianda.query.all()
    return render_template('viandas.html', viandas=lista)

@app.route('/eliminar_vianda/<int:id>')
def eliminar_vianda(id):
    v = Vianda.query.get(id)
    if v:
        db.session.delete(v)
        db.session.commit()
    return redirect(url_for('viandas'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
