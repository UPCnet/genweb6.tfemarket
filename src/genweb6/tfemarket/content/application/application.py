# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone import api
from plone.autoform import directives
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.supermodel import model
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.globalrequest import getRequest
from zope.interface import provider
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.core.widgets import ReadOnlyInputFieldWidget
from genweb6.tfemarket import _
from genweb6.tfemarket.utils import checkPermissionCreateApplications
from genweb6.tfemarket.utils import getDegreeLiteralFromId
from genweb6.tfemarket.widgets import StudentInputFieldWidget

import ast


def getCookie():
    request = getRequest()
    cookie = {}
    try:
        data = request.cookies.get('APPLICATION_DATA')
        cookie = ast.literal_eval(data)
        return cookie
    except:
        pass


@provider(IContextSourceBinder)
def getDegrees(context):
    titulacions = []
    result = getCookie()
    if result:
        degrees = result['degrees']

        for item in degrees:
            titulacions.append(SimpleTerm(value=item['degree_id'], title=item['degree_title']))
        return SimpleVocabulary(titulacions)
    else:
        if getattr(context, 'degree_id', False):
            if context.degree_id:
                titulacions.append(SimpleTerm(value=context.degree_id, title=context.degree_title))
                return SimpleVocabulary(titulacions)
            else:
                context.plone_utils.addPortalMessage(_(u"Comprova que la teva titulació correspon a la titulació per a la qual s'oferta el treball"), 'error')
        else:
            titulacions.append(SimpleTerm(value='None', title=''))
            return SimpleVocabulary(titulacions)


class IApplication(model.Schema):
    """ Application for an offer
    """
    directives.mode(degree_title='hidden')
    degree_title = schema.TextLine(
        title=_(u'Title of the degree with which you request the offer'),
        required=False,
    )

    directives.mode(IEditForm, degree_id='display')
    degree_id = schema.Choice(
        title=_(u'Title of the degree with which you request the offer'),
        source=getDegrees,
        required=True,
    )

    directives.widget('offer_id', ReadOnlyInputFieldWidget)
    offer_id = schema.TextLine(
        title=_(u'Offer id'),
        required=True,
    )

    directives.widget('offer_title', ReadOnlyInputFieldWidget)
    offer_title = schema.TextLine(
        title=_(u'Offer title'),
        required=True,
    )

    directives.widget('dni', ReadOnlyInputFieldWidget)
    dni = schema.TextLine(
        title=_(u'DNI'),
        required=True,
    )

    directives.widget('title', StudentInputFieldWidget)
    title = schema.TextLine(
        title=_(u'Fullname'),
        required=True,
    )

    phone = schema.TextLine(
        title=_(u"Telephone"),
        required=False,
    )

    directives.widget('email', ReadOnlyInputFieldWidget)
    email = schema.TextLine(
        title=_(u'Email'),
        required=True,
    )

    directives.mode(prisma_id='hidden')
    prisma_id = schema.TextLine(
        title=_(u'PRISMA id'),
        required=False,
    )

    directives.mode(codi_expedient='hidden')
    codi_expedient = schema.TextLine(
        title=_(u'Codi Expedient'),
        required=False,
    )

    body = schema.Text(
        title=_(u'Body'),
        required=False,
    )


class View(BrowserView):

    def redirectToMarket(self):
        roles = api.user.get_current().getRoles()
        market_path = self.context.getParentNode().getParentNode().absolute_url()
        if 'Manager' in roles or 'TFE Manager' in roles:
            self.request.response.redirect(market_path + "?searchOffer&offer=" + self.context.offer_id + "&open=Y")
        else:
            self.request.response.redirect(market_path)


class AddForm(add.DefaultAddForm):
    portal_type = 'genweb.tfemarket.application'

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        lang = self.request.get("MERCAT_TFE_LANG", 'ca')
        if lang in ['ca', 'en', 'es']:
            self.request['LANGUAGE'] = lang
            self.request.LANGUAGE_TOOL.LANGUAGE = lang

        if not checkPermissionCreateApplications(self, self.context, False):
            self.context.plone_utils.addPortalMessage(_(u"You have already created an application. You can see it on the main page of the market."), 'error')
            self.request.response.redirect(self.context.absolute_url())


class AddView(add.DefaultAddView):
    form = AddForm


class EditForm(edit.DefaultEditForm):

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        lang = self.request.get("MERCAT_TFE_LANG", 'ca')
        if lang in ['ca', 'en', 'es']:
            self.request['LANGUAGE'] = lang
            self.request.LANGUAGE_TOOL.LANGUAGE = lang

        if not checkPermissionCreateApplications(self, self.context, False):
            self.context.plone_utils.addPortalMessage(_(u"You have already created an application. You can see it on the main page of the market."), 'error')
            self.request.response.redirect(self.context.absolute_url())


def defineDregreecode(application, event):
    application.degree_title = getDegreeLiteralFromId(application.degree_id)
    application.reindexObject()


def getCodiExpedient(application, event):
    result = getCookie()
    degrees = result['degrees']
    codiexpedient = (item['codi_expedient'] for item in degrees if item['degree_id'] == application.degree_id)

    for x in codiexpedient:
        application.codi_expedient = x

    application.reindexObject()
    request = getRequest()
    request.response.expireCookie('APPLICATION_DATA', path='/')
