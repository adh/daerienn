from markupsafe import Markup

def xmlattrs(attrs):
    res = Markup(" ").join(
        Markup('{0}="{1}"').format(k, v) 
        for k, v in attrs.items()
        if v != None
    )
    if res != '':
        return " " + res
    else:
        return ""

def xmltag(name, attrs):
    return Markup("<{0}{1}>").format(name, xmlattrs(attrs))

def element(name, attrs, contents):
    return Markup("{0}{1}</{2}>").format(xmltag(name, attrs),
                                         contents,
                                         name)
