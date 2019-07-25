from flask import current_app, Blueprint, url_for
from daerienn.toplevel import DummySessionProvider
import time
import os

blueprint = Blueprint("daerienn", __name__)

import pkg_resources
def res(f):
    return pkg_resources.resource_filename(pkg_resources.Requirement.parse('daerienn'), "daerienn/" + f)


class Daerienn:
    def __init__(self, app=None, session_provider=None):
        if session_provider is None:
            session_provider = DummySessionProvider
        self.session_provider = session_provider
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['daerienn'] = self

        bp = Blueprint('daerienn', __name__, 
                       template_folder='templates',
                       static_folder='static',
                       static_url_path=app.static_url_path + '/daerienn')
        app.register_blueprint(bp)

        @app.context_processor
        def daerienn_js_url():
            f = res('static/daerienn.js')
            
            return {"daerienn_js_url":
                    url_for("daerienn.static",
                            filename="daerienn.js",
                            v=int(os.stat(f).st_mtime))}
