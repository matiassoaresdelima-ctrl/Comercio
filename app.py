
import os
import logging
import traceback
from flask import Flask, render_template, request, redirect, url_for
from models import db, Vianda, MovimientoDinero

app = Flask(__name__)
app.config['SECRET_KEY'] = 'debug_key_999'
app.config['PROPAGATE_EXCEPTIONS'] = True

# Configurar logging para que aparezca en Render Logs
logging.basicConfig(level=logging.DEBUG)

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/ping')
def ping():
    return "OK"

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
        app.logger.error(f"Error en Dashboard: {traceback.format_exc()}")
        return f"Error detectado: {e}", 500

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creando tablas: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
