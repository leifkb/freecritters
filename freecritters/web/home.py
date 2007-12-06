# -*- coding: utf-8 -*-

from freecritters.web.form import Form, TextField, ColorSelector, SubmitButton

form = Form(u'post', 'home',
    TextField(u'asdf', u'ASDf'),
    ColorSelector(u'aj', u'DJFDS'),
    SubmitButton(title=u'PRESS ME!!!1', id_=u'submit'))

def home(req):
    f = form(req)
    if f.successful:
        print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n', '--------------------------------------------------------', f[u'asdf'], f[u'aj']
    else:
        return req.render_template('home.mako', form=f)