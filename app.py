
import os
import sys
print(">>> INICIANDO APLICACION FLASK <<<")

from flask import Flask, render_template
from models import db, Vianda, MovimientoDinero

app = Flask(__name__)
app.config['SECRET_KEY'] = 'emergency_key'

uri = os.environ.get('DATABASE_URL')
if uri and uri.startswith('postgres://'):
    uri = uri.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    print(">>> SOLICITUD RECIBIDA EN / <<<")
    return "<h1>Servidor Activo</h1><p>Si ves esto, Flask funciona. El problema era el Dashboard.</p>"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
