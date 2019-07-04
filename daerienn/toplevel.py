from flask import request, abort, jsonify
from .widgets import Widget, ProcessingContext, WidgetList
from markupsafe import Markup
from .markup import element
import pickle
import base64
import os
import json

class TopLevel(WidgetList):
    __transient_attrs__ = {
        "fragment": None,
        "event_trigger": None,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.instance_id = base64.urlsafe_b64encode(os.urandom(15)).decode('ascii')
        self.initialize_widgets()
        
    def initialize_widgets(self):
        pass
        
    def process_request(self, data, context):
        if data.get('dae-form-instance') != self.instance_id:
            return abort(400)
        super().process_request(data, context)

    def render(self, context):
        contents = []
        contents.append(
            Markup('<input type="hidden" name="{}" value="{}">')
            .format("dae-form-instance", self.instance_id)
        )
        
        for k,v in context.session.hidden_data.items():
            contents.append(
                Markup('<input type="hidden" name="{}" value="{}">')
                .format(k, v)
            )

        for i in self.children:
            contents.append(i.render(context))
            
        contents = Markup('').join(contents)
        
        return element('form',
                       {"id": self.id,
                        "method": "POST",
                        "class": "dae-toplevel",
                        "content-type": "multipart/form-data"},
                       contents)

class XHRResponse:
    def __init__(self):
        self.contents = []

    def get(self):
        return jsonify(self.contents)

    def replace_element(self, id, val):
        self.contents.append({
            "op": "replace",
            "id": id,
            "v": str(val)
        })
    
class Session:
    def __init__(self, toplevel_constructor):
        if request.method == 'POST':
            self.toplevel = self.reload_toplevel(request.form['dae-session'])
        else:
            self.toplevel = toplevel_constructor()

        self.init_context()
            
    def reload_toplevel(self, data):
        return pickle.loads(base64.b64decode(data.encode('ascii')))

    def init_context(self):
        self.context = ProcessingContext(toplevel=self.toplevel,
                                         session=self)

    def dump(self):
        return base64.b64encode(pickle.dumps(self.toplevel)).decode('ascii')
        
    @property
    def hidden_data(self):
        return {"dae-session": self.dump()}

    def __html__(self):
        return self.toplevel.render(self.context)

    def process_on_submit(self):
        if request.method == 'POST':
            self.toplevel.process_request(request.form, self.context)
            self.toplevel.update_state(self.context)
            return True
        return False

    def __getitem__(self, name):
        return self.context.binding_map[name]
        
    def __enter__(self):
        self.process_on_submit()
        return self

    def __exit__(self, type=None, value=None, traceback=None):
        pass

    def is_xhr(self):
        return "dae-xhr-trigger" in request.form

    def handle_xhr(self):
        output = XHRResponse()
        self.toplevel.render_diff(output, self.context)
        return output.get()
