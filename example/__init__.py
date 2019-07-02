from flask import Flask, Blueprint, flash, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("page.html")
