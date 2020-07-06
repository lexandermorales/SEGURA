from flask import Flask, render_template, request, redirect, url_for
from automation_access import obtener_tweets
from modelling import prediction
import csv
import pandas as pd
import numpy as np
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length, NumberRange
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config['SECRET_KEY'] = 'EstaEsUnaClaveParaElProyectoSeguraAI'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@127.0.0.1:5432/segura'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class user_administration(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    last_name = db.Column(db.String(40))
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    testimonio = db.Column(db.String())
    edad = db.Column(db.Integer)
    residencia = db.Column(db.String())
    perfil_del_acosador = db.Column(db.String(15))


@login_manager.user_loader
def load_user(user_id):
    return user_administration.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
        InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
        InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    name = StringField('name', validators=[
                       InputRequired(), Length(min=4, max=15)])
    last_name = StringField('last_name', validators=[
                            InputRequired(), Length(min=4, max=50)])
    username = StringField('username', validators=[
        InputRequired(), Length(min=4, max=15)])
    email = StringField('email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    password = PasswordField('password', validators=[
        InputRequired(), Length(min=8, max=80)])

    testimonio = StringField('denuncia', validators=[
                             InputRequired(), Length(min=4, max=200)])
    edad = IntegerField('edad', validators=[
        InputRequired(), NumberRange(min=1, max=60)])
    residencia = StringField('residencia', validators=[
        InputRequired(), Length(min=4, max=30)])
    perfil_del_acosador = StringField('acosador', validators=[
        InputRequired(), Length(min=4, max=15)])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = user_administration.query.filter_by(
            username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = user_administration(name=form.name.data, last_name=form.last_name.data, username=form.username.data,
                                       email=form.email.data, password=hashed_password, testimonio=form.testimonio.data, edad=form.edad.data, residencia=form.residencia.data, perfil_del_acosador=form.perfil_del_acosador.data)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        # return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/mining', methods=['POST', 'GET'])
@login_required
def mining():
    if request.method == "POST":
        palabra = request.form.get('palabra')
        cantidad = request.form.get('cantidad')
        if int(cantidad) > 4000:
            return '<h1>Coloque una cantidad menor que 400</h1>'
        return redirect(url_for('visualizar', palabra=palabra, cantidad=cantidad))

    return render_template('mining.html')


@app.route('/visualizar/<palabra>/<cantidad>', methods=['POST', 'GET'])
@login_required
def visualizar(palabra, cantidad):
    cantidad = int(cantidad)
    data = obtener_tweets(palabra, cantidad)
    data = pd.DataFrame(data)
    data.columns = [['Id', 'Nombre', 'Usuario', 'Texto', 'Fecha', 'Lugar']]
    table = data.to_html(
        classes=["table-bordered", "table-striped", "table-hover"], border=0)

    if request.method == 'POST':
        if request.form['submit_button'] == 'adelante':
            return redirect(url_for('bad', cantidad=cantidad, palabra=palabra, data=data))
        elif request.form['submit_button'] == 'atras':
            return redirect(url_for('mining'))
        else:
            return "Coloca los datos correctos nuevamente"
    return render_template('visualization.html', table=table)


@app.route('/bad/<palabra>/<cantidad>', methods=['POST', 'GET'])
@login_required
def bad(palabra, cantidad):
    cantidad = int(cantidad)
    data = obtener_tweets(palabra, cantidad)
    bad_coments = prediction(palabra, cantidad)
    bad_coments = pd.DataFrame(bad_coments)
    data = pd.DataFrame(data)
    result = pd.concat([data, bad_coments], axis=1)
    result.columns = [['Id', 'Nombre', 'Usuario',
                       'Texto', 'Fecha', 'Lugar', 'Sentimiento']]
    table_bad_comments = result.to_html(
        classes=["table-bordered", "table-striped", "table-hover"], border=0)
    if request.method == 'POST':
        if request.form['submit_button'] == 'atras':
            return redirect(url_for('visualizar', palabra=palabra, cantidad=cantidad))

    return render_template('bad.html', table_pred=table_bad_comments)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
