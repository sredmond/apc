from flask import render_template, flash, redirect, url_for
from app import app
from os import urandom
from datetime import datetime
    
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
        title = 'Home')

@app.route('/loghw')
def me():
    return render_template('loghw.html',
        title="Class Log and HW")