from flask import Flask, Blueprint, flash, render_template
from daerienn import Session, StaticText, TopLevel
from daerienn.widgets import TextInput, Button
app = Flask(__name__)

class HelloWorld(TopLevel):
    def initialize_widgets(self):
        self.append(StaticText(text="Hello, world", name="label"))
        self.append(TextInput(name="input"))
        self.append(Button(text="OK"))
    
@app.route('/', methods=["GET", "POST"])
def index():
    s = Session(HelloWorld)
    
    if s.process_on_submit():
        s["label"].text = "Hello, {}".format(s["input"].value)
        
    return render_template("page.html", d=s)
