from flask import current_app, Blueprint, url_for
import time

blueprint = Blueprint("daerienn", __name__)

class Daerienn:
    def __init__(self, app=None):
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
            return {"daerienn_js_url":
                    url_for("daerienn.static", filename="daerienn.js")+"?"+str(time.time())}
