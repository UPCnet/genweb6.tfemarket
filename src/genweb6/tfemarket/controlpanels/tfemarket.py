# -*- coding: utf-8 -*-
from Products.statusmessages.interfaces import IStatusMessage

from collective.z3cform.datagridfield.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield.registry import DictRow
from plone.app.registry.browser import controlpanel
from plone.autoform import directives
from plone.autoform.directives import read_permission
from plone.autoform.directives import write_permission
from plone.supermodel import model
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from zope import schema
from zope.interface import implementer
from zope.ramcache import ram
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

from genweb6.tfemarket import _


class ITableTitulacions(model.Schema):

    codi_prisma = schema.TextLine(
        title=_(u'PRISMA code'),
        required=False,
        description=_(u'Degree code at PRISMA')
    )

    progam_type = schema.TextLine(
        title=_(u'Program type'),
        required=False
    )

    codi_mec = schema.TextLine(
        title=_(u'MEC code'),
        required=False,
        description=_(u'MEC degree code')
    )

    plan_year = schema.TextLine(
        title=_(u'Plan year'),
        required=False,
    )

    titulacio_es = schema.TextLine(
        title=_(u'Titulacions ES'),
        description=_(u''),
        required=False
    )

    titulacio_ca = schema.TextLine(
        title=_(u'Titulacions CA'),
        description=_(u''),
        required=False
    )

    titulacio_en = schema.TextLine(
        title=_(u'Titulacions EN'),
        description=_(u''),
        required=False
    )


@implementer(IVocabularyFactory)
class EnrollVocabulary(object):

    def __call__(self, context):
        types = []
        types.append(SimpleVocabulary.createTerm(u'I', 'I', _(u'Enroll')))
        types.append(SimpleVocabulary.createTerm(u'R', 'R', _(u'Register')))
        return SimpleVocabulary(types)


@implementer(IVocabularyFactory)
class AllLanguageVocabulary(object):

    def __call__(self, context):
        languages = []
        languages.append(SimpleVocabulary.createTerm(u'CA', 'CA', _(u'CA')))
        languages.append(SimpleVocabulary.createTerm(u'ES', 'ES', _(u'ES')))
        languages.append(SimpleVocabulary.createTerm(u'EN', 'EN', _(u'EN')))
        languages.append(SimpleVocabulary.createTerm(u'FR', 'FR', _(u'FR')))
        return SimpleVocabulary(languages)


class ITfemarketSettings(model.Schema):
    """ Global TFE Market settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    model.fieldset(
        'Settings',
        _(u'Settings'),
        fields=['center_code', 'center_name', 'review_state', 'enroll_type', 'alternative_email',
                'alternative_email_name'],
    )

    model.fieldset(
        'Titulacions',
        _(u'Titulacions'),
        fields=['titulacions_table'],
    )

    model.fieldset(
        'Ofertes',
        _(u'Ofertes'),
        fields=['life_period', 'view_num_students', 'import_offers', 'count_offers']
    )

    model.fieldset(
        'TopicTFE',
        _(u'classifications'),
        fields=['topics', 'tags', 'languages'],
    )

    model.fieldset(
        'Migration',
        _(u'Migració'),
        fields=['enable_suscribers'],
    )

    # SETTINGS

    center_code = schema.Int(
        title=_(u'Center code'),
        required=False,
        description=_(u'Center code')
    )

    center_name = schema.TextLine(
        title=_(u"Name center"),
        required=False,
    )

    review_state = schema.Bool(
        title=_(u"Review State"),
        default=False,
        description=_(u'Select if you want to add "Reviewer" role'),
        required=False,
    )

    enroll_type = schema.Choice(
        title=_(u'Enroll type '),
        description=_('Parameter to post the student enroll'),
        vocabulary=u"genweb.tfemarket.Enrolls",
        default=u'I',
        required=True)

    alternative_email = schema.TextLine(
        title=_(u"Alternative email"),
        description=_(u'If this field is not filled in, the default Genweb email will be taken'),
        required=False,
    )

    alternative_email_name = schema.TextLine(
        title=_(u"Alternative email name"),
        description=_(u'If this field is not filled in, the default Genweb email name will be taken'),
        required=False,
    )

    # CLASSIFICATIONS

    topics = schema.Text(
        title=_(u"Topics of the TFE"),
        description=_(u'Add topics one per line'),
        required=False,
    )

    tags = schema.Text(
        title=_(u"Tags"),
        description=_(u'Add tags one per line'),
        required=False,
    )

    directives.widget(languages=CheckBoxFieldWidget)
    languages = schema.List(
        title=_(u"Development languages"),
        description=_(u'Add languages one per line'),
        value_type=schema.Choice(source=u"genweb.tfemarket.AllLanguages"),
        required=False,
    )

    # TITULACIONS

    directives.widget(titulacions_table=DataGridFieldFactory)
    titulacions_table = schema.List(
        title=_(u'Titulacions'),
        description=_(u'help_titulacions_table', default=u'Imported dades from csv'),
        value_type=DictRow(schema=ITableTitulacions),
        required=False,
    )

    # OFERTES

    life_period = schema.Int(
        title=_(u'Months until expiration'),
        description=_('Months until the offer expires automatically'),
        required=True,
        default=12,
    )

    view_num_students = schema.Bool(
        title=_(u'View number of students'),
        description=_('Uncheck this option if you do not want to see the number of students in an offer'),
        required=False,
        default=True,
    )

    directives.mode(import_offers='display')
    import_offers = schema.Text(
        title=_(u"Import offers"),
        description=_(u'To import the offers access the following <a href=\"import_ofertes\">link</a>.'),
        required=False,
    )

    directives.mode(count_offers='display')
    count_offers = schema.Int(
        title=_(u"Number of offers created"),
        description=_(u'To reset the counter access the following <a href=\"reset_offers_counter\">link</a>.'),
        required=False,
        default=0,
    )

    # MIGRACIO

    read_permission(enable_suscribers='genweb.webmaster')
    write_permission(enable_suscribers='genweb.manager')
    enable_suscribers = schema.Bool(
        title=_(u'Habilitar notificacions'),
        required=False,
        default=False,
    )


class TfemarketSettingsEditForm(controlpanel.RegistryEditForm):

    schema = ITfemarketSettings
    label = _(u'UPC Mercat TFE')

    def updateFields(self):
        super(TfemarketSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(TfemarketSettingsEditForm, self).updateWidgets()

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        ram.caches.clear()
        self.applyChanges(data)

        IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(self.context.absolute_url() + '/' + self.control_panel_view)


class TfemarketSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TfemarketSettingsEditForm
