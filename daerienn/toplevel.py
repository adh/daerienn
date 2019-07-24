from flask import request, abort, jsonify, current_app
from .widgets import Widget, ProcessingContext, WidgetList
from markupsafe import Markup
from .markup import element
import pickle
import base64
import os
import json

class TopLevel(Widget):
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

    @property
    def session_element_id(self):
        return "{}-session".format(self.id)
        
    def render(self, context):
        contents = []
        contents.append(
            Markup('<input type="hidden" name="{}" value="{}">')
            .format("dae-form-instance", self.instance_id)
        )
        
        contents.append(
            Markup('<input type="hidden" name="dae-session" value="{}" id="{}">')
            .format(context.session.session_data, self.session_element_id)
        )

        contents.append(super().render(context))
            
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

    def redirect(self, url):
        self.contents.append({
            "op": "redirect",
            "url": url
        })

    def set_value(self, id, value):
        self.contents.append({
            "op": "value",
            "id": id,
            "v": str(value)
        })
        
        
    
class Session:
    def __init__(self, toplevel_constructor, session_provider=None):
        if session_provider is None:
            session_provider = current_app.extensions['daerienn'].session_provider
        self.session_provider = session_provider

        self.session_id = None
        
        if request.method == 'POST':
            session = request.form['dae-session']
            self.toplevel = self.reload_toplevel(session)
            if session_provider.__persistent__:
                self.session_id = session
        else:
            self.toplevel = toplevel_constructor()

        self.init_context()
            
    def reload_toplevel(self, data):
        return pickle.loads(self.session_provider.load(data))

    def init_context(self):
        self.context = ProcessingContext(toplevel=self.toplevel,
                                         session=self)

    def dump(self):
        return self.session_provider.store(pickle.dumps(self.toplevel,
                                                        protocol=pickle.HIGHEST_PROTOCOL),
                                           session_id=self.session_id)
        

    @property
    def session_data(self):
        return self.dump()
    
    def __html__(self):
        self.handle_xhr()
        return self.toplevel.render(self.context)

    def __call__(self):
        return self.__html__()
    
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

    def xhr_response(self):
        output = XHRResponse()
        self.toplevel.render_diff(output, self.context)
        if not self.session_provider.__persistent__:
            output.set_value(self.toplevel.session_element_id, self.dump())
        else:
            self.dump()
        return output.get()

    def handle_xhr(self):
        if self.is_xhr():
            res = self.xhr_response()
            abort(res)
        
    def redirect(self, url):
        if self.is_xhr():
            output = XHRResponse()
            output.redirect(url)
            abort(output.get())
        else:
            redirect(url)

class SessionProvider:
    __persistent__ = False
    def load(self, key):
        raise NotImplemented
    def store(self, data, session_id=None):
        raise NotImplemented

class DummySessionProvider(SessionProvider):
    def load(self, key):
        return base64.b64decode(key.encode('ascii'))
    def store(self, data, session_id=None):
        return base64.b64encode(data).decode('ascii')

