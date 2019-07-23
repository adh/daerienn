from .state import Persistent
import base64
import os
from markupsafe import Markup, escape
import shortuuid
from .markup import element, xmltag

class ProcessingContext:
    def __init__(self, session=None, toplevel=None, binding_map=None):
        if binding_map is None:
            binding_map = {}
        self.session = session
        self.toplevel = toplevel
        self.binding_map = binding_map

    def bind_widget(self, name, widget):
        self.binding_map[name] = widget

    def __getitem__(self, name):
        return self.binding_map[name]

class Widget(Persistent):
    __transient_attrs__ = {
        "dirty": False
    }
    
    def __init__(self,
                 name=None):
        super().__init__()
        self.name = name
        self.id = self.generate_id()
        self.dirty = True

    @classmethod
    def generate_id(cls):
        return "w"+shortuuid.uuid()
        
    def process_request(self, data, context):
        if self.name:
            context.bind_widget(self.name, self)
        
    def update_state(self, context):
        pass

    def render(self, context):
        return self.__html__()

    def render_diff(self, output, context):
        if self.dirty:
            output.replace_element(self.id, self.render(context))

class WidgetCollection(Widget):
    def process_request(self, data, context):
        super().process_request(data, context)
        for i in self.children:
            i.process_request(data, context)
            
    def update_state(self, context):
        for i in self.children:
            i.update_state(context)

    def render_diff(self, output, context):
        if self.dirty:
            output.replace_element(self.id, self.render(context))
        else:
            for i in self.children:
                i.render_diff(output, context)

class WidgetList(WidgetCollection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.children = []
        
    def append(self, widget):
        self.children.append(widget)
        self.dirty = True

    def render(self, context):
        return Markup('').join(i.render(context) for i in self.children)

class ValueWidget(Widget):
    def __init__(self, value=None, **kwargs):
        super().__init__(**kwargs)
        self._value = value
        
    def get_value(self):
        return self._value
 
    def set_value(self, value):
        self._value = value
        self.dirty = True
        
    value = property(get_value, set_value)    
    
class StaticText(Widget):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self._text = text
        
    def get_text(self):
        return self._text
 
    def set_text(self, text):
        self._text = text
        self.dirty = True
        
    text = property(get_text, set_text)    

    def __html__(self):
        return element("span", {"id": self.id}, self._text)


class InputWidget(ValueWidget):
    __transient_attrs__ = {
        "raw_value": None
    }
    
    def process_request(self, data, context):
        super().process_request(data, context)
        if self.id in data:
            self.raw_value = data[self.id]
            self._value = self.deserialize_value(data[self.id])

    def deserialize_value(self, val):
        return val
    def serialize_value(self, val):
        return val
            
    def __html__(self):
        if self.dirty:
            val = self.serialize_value(self.value)
        else:
            val = self.raw_value
        
        return xmltag("input",
                       {"type": self.input_type,
                        "id": self.id,
                        "name": self.id,
                        "value": val})
            
class TextInput(InputWidget):
    input_type = "text"

class Button(StaticText):
    def __html__(self):
        return element("button",
                       {"type": "submit",
                        "id": self.id,
                        "name": self.id,
                        "value": self.id},
                       self._text)
    
