
import os
import traceback
from flask import Flask, render_template, request, redirect, url_for
from models import db, Vianda, MovimientoDinero

app = Flask(__name__)
app.config['SECRET_KEY'] = 'diagnostico_123'

# Prioridad absoluta a la URL de Render
uri = os.environ.get('DATABASE_URL')
if uri:
    if uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
else:
    uri = 'sqlite:///comercio.db'

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/ping')
def ping():
    return "Flask está vivo. URL de DB configurada: " + ("Sí" if os.environ.get('DATABASE_URL') else "No (usando SQLite local)")

@app.route('/test_db')
def test_db():
    try:
        with app.app_context():
            db.create_all()
            count = Vianda.query.count()
        return f"Conexión OK. Viandas en DB: {count}"
    except Exception as e:
        return f"Error de conexión a DB: {str(e)}<br><pre>{traceback.format_exc()}</pre>"

@app.route('/')
def index():
    try:
        from datetime import datetime
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0)
        v_mes, g_mes, balance, conteo_ventas = MovimientoDinero.get_financial_summary(inicio_mes)
        stats = {
            'v_mes': v_mes, 'g_mes': g_mes, 'balance': balance,
            'cant_viandas': Vianda.query.count(),
            'margen': round((balance / v_mes * 100) if v_mes > 0 else 0, 1),
            'ticket_promedio': round((v_mes / conteo_ventas) if conteo_ventas > 0 else 0, 2),
            'fecha_mes': inicio_mes.strftime('%d/%m/%Y')
        }
        return render_template('dashboard.html', **stats)
    except Exception as e:
        return f"<h1>Error en Dashboard</h1><pre>{traceback.format_exc()}</pre>", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
