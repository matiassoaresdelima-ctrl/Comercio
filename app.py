
import os
import sys
import logging
import traceback

# Intentar capturar el error exacto de importación o configuración
try:
    from flask import Flask
    from models import db

    app = Flask(__name__)
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///comercio.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.route('/')
    def index():
        return "<h1>Diagnóstico: Sistema Operativo</h1>"

    if __name__ == '__main__':
        with app.app_context():
            db.create_all()
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

except Exception as e:
    print("!!! ERROR CRITICO EN EL ARRANQUE !!!")
    traceback.print_exc(file=sys.stdout)
    sys.exit(1)
