
import os
import traceback
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import db, Vianda, MovimientoDinero

app = Flask(__name__)
app.config['SECRET_KEY'] = 'prod_key_999'
uri = os.environ.get('DATABASE_URL', 'sqlite:///comercio.db')
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    try:
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
    except Exception as e:
        error_details = traceback.format_exc()
        return f"<h1>Error de Diagnóstico</h1><p>{e}</p><pre>{error_details}</pre>", 500

@app.route('/viandas', methods=['GET', 'POST'])
def viandas():
    if request.method == 'POST':
        nueva = Vianda(nombre=request.form.get('nombre'), precio=float(request.form.get('precio', 0)), disponible=True)
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
