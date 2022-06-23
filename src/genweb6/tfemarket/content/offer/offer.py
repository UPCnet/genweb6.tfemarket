# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from operator import itemgetter
from plone import api
from plone.autoform import directives
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.indexer import indexer
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.tfemarket import _
from genweb6.tfemarket.controlpanels.tfemarket import ITfemarketSettings
from genweb6.tfemarket.widgets import CodirectorInputFieldWidget
from genweb6.tfemarket.widgets import FieldsetFieldWidget
from genweb6.tfemarket.widgets import ReadOnlyInputFieldWidget
from genweb6.tfemarket.widgets import SelectModalityInputFieldWidget
from genweb6.tfemarket.widgets import TeacherInputFieldWidget

import transaction
import unicodedata


@implementer(IVocabularyFactory)
class LangsVocabulary(object):

    def __call__(self, context):
        registry = queryUtility(IRegistry)
        tfe_tool = registry.forInterface(ITfemarketSettings)
        results = tfe_tool.languages

        lang = api.portal.get_current_language()

        languages = []
        for item in results:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
            itemTranslate = translate(msgid=item, domain='genweb.tfemarket', target_language=lang)
            languages.append(SimpleVocabulary.createTerm(item, flattened, itemTranslate))

        return SimpleVocabulary(languages)


@implementer(IVocabularyFactory)
class KeysVocabulary(object):

    def __call__(self, context):
        registry = queryUtility(IRegistry)
        tfe_tool = registry.forInterface(ITfemarketSettings)
        results = []
        tags = []

        keys = tfe_tool.tags
        if keys:
            results = keys.split("\r\n")

        for item in results:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
            tags.append(SimpleVocabulary.createTerm(item, flattened, item))

        return SimpleVocabulary(tags)


@implementer(IVocabularyFactory)
class TopicsVocabulary(object):

    def __call__(self, context):
        registry = queryUtility(IRegistry)
        tfe_tool = registry.forInterface(ITfemarketSettings)
        results = []
        topic = []

        topics = tfe_tool.topics
        if topics:
            results = topics.split("\r\n")

        for item in results:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
            topic.append(SimpleVocabulary.createTerm(item, flattened, item))

        return SimpleVocabulary(topic)


@implementer(IVocabularyFactory)
class OfferTypesVocabulary(object):

    def __call__(self, context):
        types = []
        types.append(SimpleVocabulary.createTerm(u'Study', 'Study', _(u'Study')))
        types.append(SimpleVocabulary.createTerm(u'Project', 'Project', _(u'Project')))
        types.append(SimpleVocabulary.createTerm(u'Design', 'Design', _(u'Design')))
        types.append(SimpleVocabulary.createTerm(u'Others', 'Others', _(u'Others')))
        return SimpleVocabulary(types)


@implementer(IVocabularyFactory)
class TFGMVocabulary(object):

    def __call__(self, context):
        types = []
        types.append(SimpleVocabulary.createTerm(u'TFG', 'TFG', u'TFG'))
        types.append(SimpleVocabulary.createTerm(u'TFM', 'TFM', u'TFM'))
        return SimpleVocabulary(types)


@implementer(IVocabularyFactory)
class ModalityVocabulary(object):

    def __call__(self, context):
        types = []
        types.append(SimpleVocabulary.createTerm(u'Universitat', 'Universitat', _(u'Universitat')))
        # types.append(SimpleVocabulary.createTerm(u'Empresa', 'Empresa', _(u'Empresa')))
        return SimpleVocabulary(types)


@implementer(IVocabularyFactory)
class DegreesVocabulary(object):

    def __call__(self, context):
        registry = queryUtility(IRegistry)
        tfe_tool = registry.forInterface(ITfemarketSettings)
        current_language = api.portal.get_current_language()

        result = []
        titulacions = []

        for item in tfe_tool.titulacions_table:
            titulacio = str(item['plan_year']) + " - "
            if current_language == 'ca':
                titulacio += item['titulacio_ca']
            elif current_language == 'es':
                titulacio += item['titulacio_es']
            else:
                titulacio += item['titulacio_en']

            result.append({'id': item['codi_mec'], 'lit': titulacio})

        result = sorted(result, key=itemgetter('lit'))

        for item in result:
            titulacions.append(SimpleTerm(value=item['id'], title=item['lit']))

        return SimpleVocabulary(titulacions)


@implementer(IVocabularyFactory)
class TypeCodirectorVocabulary(object):

    def __call__(self, context):
        types = []
        types.append(SimpleVocabulary.createTerm(u'UPC', 'UPC', u'UPC'))
        types.append(SimpleVocabulary.createTerm(u'External', 'External', _(u'External')))
        return SimpleVocabulary(types)


class IOffer(model.Schema):
    """ Folder that contains information about a TFE and its applications
    """

    directives.mode(center='hidden')
    center = schema.TextLine(
        title=_(u'offer_center'),
        required=False,
    )

    directives.mode(offer_id="hidden")
    offer_id = schema.TextLine(
        title=_(u'Offer id'),
        required=False,
    )

    title = schema.TextLine(
        title=_(u'Title'),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        description=_(u'Breu explicació dels aspectes bàsics del treball'),
        required=True,
    )

    targets = schema.Text(
        title=_(u'offer_targets'),
        description=_(u'Resultat esperat d’aquest treball'),
        required=False,
    )

    features = schema.Text(
        title=_(u'offer_features'),
        required=False,
    )

    topic = schema.Choice(
        title=_(u'offer_topic'),
        vocabulary=u"genweb.tfemarket.Topics",
        required=False
    )

    offer_type = schema.Choice(
        title=_(u'offer_type'),
        vocabulary=u"genweb.tfemarket.OfferTypes",
        default=_(u'Project'),
        required=False
    )

    directives.widget(tfgm=CheckBoxFieldWidget)
    tfgm = schema.List(
        value_type=schema.Choice(source=u"genweb.tfemarket.TFGM"),
        title=_(u'tfgm'),
        required=True,
    )

    directives.widget(degree=CheckBoxFieldWidget)
    degree = schema.List(
        value_type=schema.Choice(source=u"genweb.tfemarket.Titulacions"),
        title=_(u'degree'),
        required=True,
    )

    directives.widget(keys=CheckBoxFieldWidget)
    keys = schema.List(
        value_type=schema.Choice(source=u"genweb.tfemarket.Keys"),
        title=_(u'keys'),
        required=False,
    )

    ############################################################################

    directives.widget('fieldset_dir', FieldsetFieldWidget)
    fieldset_dir = schema.Text(
        default=_(u'Direction'),
        required=False,
    )

    directives.widget('teacher_manager', TeacherInputFieldWidget)
    teacher_manager = schema.TextLine(
        title=_(u'TFEteacher'),
        required=True,
    )

    directives.widget('teacher_fullname', ReadOnlyInputFieldWidget)
    teacher_fullname = schema.TextLine(
        title=_(u'Teacher Fullname'),
        required=False,
    )

    directives.widget('teacher_email', ReadOnlyInputFieldWidget)
    teacher_email = schema.TextLine(
        title=_(u'Teacher Email'),
        required=False,
    )

    directives.widget('dept', ReadOnlyInputFieldWidget)
    dept = schema.TextLine(
        title=_(u'University department'),
        required=False,
    )

    type_codirector = schema.Choice(
        title=_(u'Type codirector'),
        vocabulary=u'genweb.tfemarket.TypeCodirector',
        required=False,
    )

    directives.widget('codirector_id', CodirectorInputFieldWidget)
    codirector_id = schema.TextLine(
        title=_(u'Codirector'),
        required=False,
    )

    codirector = schema.TextLine(
        title=_(u'Codirector Fullname'),
        required=False,
    )

    directives.widget('codirector_email', ReadOnlyInputFieldWidget)
    codirector_email = schema.TextLine(
        title=_(u'Codirector Email'),
        required=False,
    )

    directives.widget('codirector_dept', ReadOnlyInputFieldWidget)
    codirector_dept = schema.TextLine(
        title=_(u'Codirector University department'),
        required=False,
    )

    ############################################################################

    directives.widget('fieldset_req', FieldsetFieldWidget)
    fieldset_req = schema.Text(
        default=_(u'Other data'),
        required=False,
    )

    num_students = schema.Int(
        title=_(u'Number of students'),
        description=_(u'Màxim segons normativa del centre'),
        default=1,
        min=1,
        max=10,
        required=True,
    )

    workload = schema.TextLine(
        title=_(u'offer_workload'),
        description=_(u'Un crèdit ECTS equival a 25 hores de treball. La càrrega de treball s\'adaptarà als crèdits de la titulació.'),
        required=True,
    )

    requirements = schema.Text(
        title=_(u'requirements'),
        description=_(u'Coneixements previs necessaris per portar a terme el treball'),
        required=False,
    )

    directives.widget(lang=CheckBoxFieldWidget)
    lang = schema.List(
        value_type=schema.Choice(vocabulary=u"genweb.tfemarket.Langs"),
        title=_(u'tfe_lang'),
        required=True,
        default=['CA']
    )

    ############################################################################

    directives.widget('fieldset_mod', FieldsetFieldWidget)
    fieldset_mod = schema.Text(
        default=_(u'Modality'),
        required=False,
    )

    directives.widget('modality', SelectModalityInputFieldWidget)
    modality = schema.Choice(
        title=_(u'modality'),
        vocabulary=u"genweb.tfemarket.Modality",
        default=_(u'Universitat'),
        required=True,
    )

    company = schema.TextLine(
        title=_(u'Company'),
        required=False,
    )

    @invariant
    def validate_isFull(data):
        if data.modality == 'Empresa' and not data.company:
            raise Invalid(_(u"Falta omplir les dades d'empresa"))
        if not data.lang:
            raise Invalid(_(u'Falta omplir "Idioma del treball"'))

    ############################################################################

    directives.widget('fieldset_opt', FieldsetFieldWidget)
    fieldset_opt = schema.Text(
        default=_(u'Options'),
        required=False,
    )

    grant = schema.Bool(
        title=_(u'Possibility of scholarship'),
        required=False,
        default=False,
    )

    confidential = schema.Bool(
        title=_(u'confidential'),
        default=False,
        required=False,
    )

    environmental_theme = schema.Bool(
        title=_(u'Environmental Theme'),
        default=False,
        required=False,
    )

    scope_cooperation = schema.Bool(
        title=_(u'Scope of cooperation'),
        default=False,
        required=False,
    )


class View(BrowserView):

    def redirectToMarket(self):
        market_path = self.context.getParentNode().absolute_url()
        self.redirect(market_path + "?searchOffer&offer=" + self.context.offer_id)


class AddForm(add.DefaultAddForm):
    portal_type = 'genweb.tfemarket.oofer'

    def updateFields(self):
        super(AddForm, self).updateFields()
        lang = self.request.get("MERCAT_TFE_LANG", 'ca')
        if lang in ['ca', 'en', 'es']:
            self.request['LANGUAGE'] = lang
            self.request.LANGUAGE_TOOL.LANGUAGE = lang

        registry = queryUtility(IRegistry)
        tfe_tool = registry.forInterface(ITfemarketSettings)
        if not tfe_tool.view_num_students:
            self.fields = self.fields.omit('num_students')

    def updateWidgets(self):
        try:
            super(AddForm, self).updateWidgets()
        except ValueError as err:
            self.context.plone_utils.addPortalMessage(_("No esta correctament configurat: '%s'") % err, 'error')


class AddView(add.DefaultAddView):
    form = AddForm


class EditForm(edit.DefaultEditForm):

    def updateFields(self):
        super(EditForm, self).updateFields()
        lang = self.request.get("MERCAT_TFE_LANG", 'ca')
        if lang in ['ca', 'en', 'es']:
            self.request['LANGUAGE'] = lang
            self.request.LANGUAGE_TOOL.LANGUAGE = lang

        registry = queryUtility(IRegistry)
        tfe_tool = registry.forInterface(ITfemarketSettings)
        if not tfe_tool.view_num_students:
            self.fields = self.fields.omit('num_students')

    def updateWidgets(self):
        try:
            super(EditForm, self).updateWidgets()
        except ValueError as err:
            self.context.plone_utils.addPortalMessage(_("No esta correctament configurat: '%s'") % err, 'error')


def numOfferDefaultValue(offer, event):
    registry = queryUtility(IRegistry)
    tfe_tool = registry.forInterface(ITfemarketSettings)
    center = tfe_tool.center_code
    total = tfe_tool.count_offers + 1

    offer.offer_id = str(center) + '-' + str(total).zfill(5)
    offer.reindexObject()

    tfe_tool.count_offers += 1
    transaction.commit()


def defineTeacherAsEditor(offer, event):
    creator = getattr(offer.getOwner(), '_id', None)
    teacher = offer.teacher_manager

    for user in offer.get_local_roles():
        if user not in [creator, teacher]:
            offer.manage_delLocalRoles([user])

    offer.creators = tuple([creator, teacher])
    offer.manage_setLocalRoles(teacher, ["Owner"])
    offer.setCreators(teacher)
    offer.addCreator(teacher)
    offer.reindexObjectSecurity()
    transaction.commit()


@indexer(IOffer)
def offer_id(context):
    return context.offer_id


@indexer(IOffer)
def offer_type(context):
    return context.offer_type


@indexer(IOffer)
def tfgm(context):
    return context.tfgm


@indexer(IOffer)
def degree(context):
    return context.degree


@indexer(IOffer)
def teacher_manager(context):
    return context.teacher_manager


@indexer(IOffer)
def dept(context):
    return context.dept


@indexer(IOffer)
def company(context):
    return context.company


@indexer(IOffer)
def grant(context):
    return context.grant


@indexer(IOffer)
def modality(context):
    return context.modality


@indexer(IOffer)
def keys(context):
    return context.keys


@indexer(IOffer)
def lang(context):
    return context.lang


@indexer(IOffer)
def topic(context):
    return context.topic
