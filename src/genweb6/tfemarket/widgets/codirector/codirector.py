# -*- coding: utf-8 -*-
from plone.formwidget.autocomplete.widget import AutocompleteSelectionWidget
from zope.interface import implementer_only

import z3c.form.browser.text
import z3c.form.interfaces
import z3c.form.widget
import zope.interface
import zope.schema.interfaces


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
