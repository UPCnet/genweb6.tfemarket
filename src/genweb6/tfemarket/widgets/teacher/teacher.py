# -*- coding: utf-8 -*-
from plone import api
from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget
from zope.interface import implementer_only

import z3c.form.browser.text
import z3c.form.interfaces
import z3c.form.widget
import zope.interface
import zope.schema.interfaces


class ITeacherInputWidget(z3c.form.interfaces.ITextWidget):
    pass


@implementer_only(ITeacherInputWidget)
class TeacherInputWidget(z3c.form.browser.text.TextWidget, AutocompleteSelectionWidget):

    klass = u'teacher-input-widget'

    def update(self):
        super(z3c.form.browser.text.TextWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)

    def getId(self):
        return api.user.get_current().id

    def hasPermissions(self):
        roles = api.user.get_roles()
        return 'TFE Manager' in roles or 'Manager' in roles

    def ifTeacher(self):
        roles = api.user.get_roles()
        return 'TFE Teacher' in roles


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def TeacherInputFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, TeacherInputWidget(request))
