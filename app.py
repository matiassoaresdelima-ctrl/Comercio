
import os
import sys
import logging
from flask import Flask
from models import db

app = Flask(__name__)

# Forzar logs a la consola de Render
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    app.logger.info("Acceso a la ruta raiz exitoso")
    return "<h1>OK: El servidor responde</h1>"

@app.route('/test_db')
def test_db():
    try:
        db.session.execute(db.text('SELECT 1'))
        return "Conexion a base de datos: EXITOSA"
    except Exception as e:
        app.logger.error(f"Error de BD: {str(e)}")
        return f"Error de BD: {str(e)}", 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
