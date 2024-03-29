from flask import Flask, Blueprint, flash, render_template
from daerienn import Session, StaticText, TopLevel, Daerienn
from daerienn.redis import RedisSessionProvider
from daerienn.widgets import TextInput, Button, JinjaWidget
from flask_redis import FlaskRedis

app = Flask(__name__)
app.config['REDIS_URL'] = "redis://localhost:6379/0"
app.config['SECRET_KEY'] = "foo"
redis_client = FlaskRedis(app)
Daerienn(app, session_provider=RedisSessionProvider(redis_client))


class HelloWorld(TopLevel, JinjaWidget):
    __template_name__ = "example.html"
    
    def initialize_widgets(self):
        self.label = (StaticText(text="Hello, world", name="label"))
        self.input = (TextInput(name="input"))
        self.submit = (Button(text="OK"))
    
@app.route('/', methods=["GET", "POST"])
def index():
    s = Session(HelloWorld)
    
    if s.process_on_submit():
        s["label"].text += " Hello, {}.".format(s["input"].value)

    return render_template("page.html", d=s())
