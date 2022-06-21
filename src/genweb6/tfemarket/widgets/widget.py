# -*- coding: utf-8 -*-
from plone import api
from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget
from zope.interface import implementer_only

import z3c.form.browser.text
import z3c.form.interfaces
import z3c.form.widget
import zope.interface
import zope.schema.interfaces


class IFieldsetWidget(z3c.form.interfaces.ITextWidget):
    pass


@implementer_only(IFieldsetWidget)
class FieldsetWidget(z3c.form.browser.text.TextWidget):

    klass = u'fieldset-widget'

    def update(self):
        super(z3c.form.browser.text.TextWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def FieldsetFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, FieldsetWidget(request))


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


class ICodirectorInputWidget(z3c.form.interfaces.ITextWidget):
    pass


@implementer_only(ICodirectorInputWidget)
class CodirectorInputWidget(z3c.form.browser.text.TextWidget, AutocompleteSelectionWidget):

    klass = u'codirector-input-widget'

    def update(self):
        super(z3c.form.browser.text.TextWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def CodirectorInputFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, CodirectorInputWidget(request))


class IReadOnlyInputWidget(z3c.form.interfaces.ITextWidget):
    pass


@implementer_only(IReadOnlyInputWidget)
class ReadOnlyInputWidget(z3c.form.browser.text.TextWidget, AutocompleteSelectionWidget):

    klass = u'readonly-input-widget'

    def update(self):
        super(z3c.form.browser.text.TextWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def ReadOnlyInputFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, ReadOnlyInputWidget(request))


class IStudentInputWidget(z3c.form.interfaces.ITextWidget):
    pass


@implementer_only(IStudentInputWidget)
class StudentInputWidget(z3c.form.browser.text.TextWidget, AutocompleteSelectionWidget):

    klass = u'student-input-widget'

    def update(self):
        super(z3c.form.browser.text.TextWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def StudentInputFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, StudentInputWidget(request))


class ISelectModalityInputWidget(z3c.form.interfaces.ISelectWidget):
    pass


@implementer_only(ISelectModalityInputWidget)
class SelectModalityInputWidget(z3c.form.browser.select.SelectWidget, AutocompleteSelectionWidget):

    klass = u'select-modality-input-widget'

    def update(self):
        super(z3c.form.browser.select.SelectWidget, self).update()
        z3c.form.browser.widget.addFieldClass(self)


@zope.component.adapter(zope.schema.interfaces.IField, z3c.form.interfaces.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def SelectModalityInputFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, SelectModalityInputWidget(request))
