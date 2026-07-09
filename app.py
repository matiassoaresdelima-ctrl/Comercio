
from flask import Flask, render_template, request, redirect, url_for
from models import db, Vianda, Cliente, Pedido, MovimientoDinero
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'comercio_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///comercio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/viandas')
def viandas():
    lista = Vianda.query.all()
    return render_template('viandas.html', viandas=lista)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=port)
