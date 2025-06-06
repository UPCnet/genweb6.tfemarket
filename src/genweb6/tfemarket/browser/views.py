# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from io import StringIO
from plone import api
from plone.dexterity.utils import createContentInContainer
from plone.memoize.view import memoize
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.security import checkPermission

from genweb6.tfemarket import _
from genweb6.tfemarket.controlpanels.tfemarket import ITfemarketSettings
from genweb6.tfemarket.utils import BusError
from genweb6.tfemarket.utils import checkOfferhasAssign
from genweb6.tfemarket.utils import genwebTfemarketConfig
from genweb6.tfemarket.utils import getApplicationsFromContent
from genweb6.tfemarket.utils import getDegrees
from genweb6.tfemarket.utils import getExactUserData
from genweb6.tfemarket.utils import getStudentData
from genweb6.tfemarket.utils import getUserData
from genweb6.tfemarket.utils import isManager
from genweb6.tfemarket.utils import isTeachersOffer

import csv
import json
import logging
import transaction

logger = logging.getLogger('genweb6.tfemarket')


def redirectToMarket(self):
    try:
        from plone.protect.interfaces import IDisableCSRFProtection
        alsoProvides(self.request, IDisableCSRFProtection)
    except:
        pass

    if self.context.portal_type == 'genweb.tfemarket.offer':
        self.request.response.redirect(self.context.absolute_url() + '#offer-applications')
    elif self.context.portal_type == 'genweb.tfemarket.market':
        if 'allOffers' not in self.request.form and 'search' not in self.request.form:
            url = self.context.absolute_url()

            if 'offer' in self.request.form:
                url += "?searchOffer&offer=" + self.request.form.get('offer')

                if 'open' in self.request.form:
                    url += "&open=Y"

            self.request.response.redirect(url)
        else:
            if 'allOffers' in self.request.form:
                url = self.context.absolute_url() + "?allOffers"
            elif 'search' in self.request.form:
                url = self.context.absolute_url() + "?searchFilters"

            if 'offer' in self.request.form:
                if 'allOffers' in self.request.form or 'search' in self.request.form:
                    url += "&offer=" + self.request.form.get('offer')
                else:
                    url += "?searchOffer&offer=" + self.request.form.get('offer')

                if 'open' in self.request.form:
                    url += "&open=Y"

            self.request.response.redirect(url)
    else:
        self.request.response.redirect(self.context.absolute_url())


class changeActualState(BrowserView):

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        estat = self.request.form.get('estat')
        itemid = self.request.form.get('id')

        try:
            portal = api.portal.get()
            currentItem = portal.unrestrictedTraverse(itemid)
            isCreator = api.user.get_current().id in currentItem.creators
            if currentItem and (isTeachersOffer(currentItem.getParentNode()) or isCreator):
                if currentItem.portal_type == 'genweb.tfemarket.offer':
                    if estat in ['assign', 'assignalofertaintranet']:
                        if not checkOfferhasAssign(currentItem):
                            logger.error("Error TFE: No se puede asignar la oferta. Debe haber al menos una solicitud confirmada y las demás canceladas, rechazadas o renunciadas.")
                            self.context.plone_utils.addPortalMessage(_(u"The offer can't be assign. There must be at least one confirmed application and the others cancelled, rejected or renounced"), 'error')
                            redirectToMarket(self)
                            return None

                    wf_tool = getToolByName(self.context, 'portal_workflow')
                    tools = getMultiAdapter((self.context, self.request), name='plone_tools')
                    market = currentItem.getParentNode()
                    marketWorkflow = tools.workflow().getWorkflowsFor(market)[0]
                    marketStatus = wf_tool.getStatusOf(marketWorkflow.id, market)
                    marketState = marketWorkflow['states'][marketStatus['review_state']]

                    if (marketState.id == 'published' and estat == 'publicaalintranet') or (marketState.id == 'intranet' and estat == 'publicaloferta'):
                        logger.error("Error TFE: El mercado ha cambiado de estado y no se puede realizar la acción.")
                        self.context.plone_utils.addPortalMessage(_(u'Error you can\'t perform the action.'), 'error')
                        redirectToMarket(self)
                        return None

                wftool = getToolByName(self.context, 'portal_workflow')
                wftool.doActionFor(currentItem, estat)
                redirectToMarket(self)
            else:
                logger.error("Error TFE: No tienes permisos de professor para realizar la acción.")
                logger.error("Error TFE: isSolicitudCreator " + str(isCreator))
                logger.error("Error TFE: isOfertaCreator " + str(isTeachersOffer(currentItem.getParentNode())))
                logger.error("Error TFE: estat " + str(estat))
                logger.error("Error TFE: itemid " + str(itemid))

                self.context.plone_utils.addPortalMessage(_(u'Error you can\'t perform the action.'), 'error')
                redirectToMarket(self)
        except BusError as err:
            if isinstance(err.value, BusError):
                self.context.plone_utils.addPortalMessage(err.value.value['resultat'], 'error')
                logger.error("Error TFE PRISMA: " + err.value.value['resultat'])
            else:
                self.context.plone_utils.addPortalMessage(err.value['resultat'], 'error')
                logger.error("Error TFE PRISMA: " + err.value['resultat'])

            logger.error("Error TFE PRISMA: itemid " + str(itemid))
            redirectToMarket(self)
        except Exception as e:
            logger.error("Error TFE: No se puede realizar la accion - " + str(e))
            logger.error("Error TFE: isSolicitudCreator " + str(isCreator))
            logger.error("Error TFE: isOfertaCreator " + str(isTeachersOffer(currentItem.getParentNode())))
            logger.error("Error TFE: estat " + str(estat))
            logger.error("Error TFE: itemid " + str(itemid))

            self.context.plone_utils.addPortalMessage(_(u'Error you can\'t perform the action.'), 'error')
            redirectToMarket(self)


class getTeacher(BrowserView):

    def __call__(self):
        teachers = getUserData(self.request.form['teacher'])
        if teachers and len(teachers['identitats']) > 0:
            listTeachers = []
            for teacher in teachers['identitats']:
                for teacherInfo in teacher['uePerfil']:
                    try:
                        teacherDept = teacherInfo['ueId'] + '-' + teacherInfo['ueAcronim']

                        if 'sobrenom' in teacher and teacher['sobrenom']:
                            if 'cognom2' in teacher and teacher['cognom2']:
                                fullname = f"{teacher['cognom1'].capitalize()} {teacher['cognom2'].capitalize()}, {teacher['sobrenom'].capitalize()}"
                            else:
                                fullname = f"{teacher['cognom1'].capitalize()}, {teacher['sobrenom'].capitalize()}"
                        else:
                            if 'cognom2' in teacher and teacher['cognom2']:
                                fullname = f"{teacher['cognom1'].capitalize()} {teacher['cognom2'].capitalize()}, {teacher['nom'].capitalize()}"
                            else:
                                fullname = f"{teacher['cognom1'].capitalize()}, {teacher['nom'].capitalize()}"
                        listTeachers.append({
                            'user': teacher['commonName'],
                            'email': teacher['emailPreferent'],
                            'fullname': fullname,
                            'dept': teacherDept
                        })
                    except Exception as e:
                        pass

            return json.dumps(listTeachers)
        else:
            return None


class getExactTeacher(BrowserView):

    def __call__(self):
        teacher = getExactUserData(api.user.get_current().id)
        if teacher:
            teacherDept = teacher['uePerfil'][0]['ueId'] + '-' + teacher['uePerfil'][0]['ueAcronim']
            for perfil in teacher['uePerfil']:
                if 'PDI' in perfil['perfilId']:
                    teacherDept = perfil['ueId'] + '-' + perfil['ueAcronim']

            if 'sobrenom' in teacher:
                if 'cognom2' in teacher:
                    fullname = f"{teacher['cognom1'].capitalize()} {teacher['cognom2'].capitalize()}, {teacher['sobrenom'].capitalize()}"
                else:
                    fullname = f"{teacher['cognom1'].capitalize()}, {teacher['sobrenom'].capitalize()}"
            else:
                if 'cognom2' in teacher:
                    fullname = f"{teacher['cognom1'].capitalize()} {teacher['cognom2'].capitalize()}, {teacher['nom'].capitalize()}"
                else:
                    fullname = f"{teacher['cognom1'].capitalize()}, {teacher['nom'].capitalize()}"

            data = {
                'user': teacher['commonName'],
                'email': teacher['emailPreferent'],
                'fullname': fullname,
                'dept': teacherDept
            }
            return json.dumps(data)
        else:
            return None


class requestOffer(BrowserView):

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        itemid = self.request.form.get('id')
        portal = api.portal.get()
        currentItem = portal.unrestrictedTraverse(itemid)
        currentUser = api.user.get_current()
        data = getStudentData(self, currentItem, currentUser)
        if data:
            self.request.response.setCookie('APPLICATION_DATA', json.dumps(data), path='/')
            self.request.response.redirect(currentItem.absolute_url() + '/++add++genweb.tfemarket.application')
        else:
            redirectToMarket(self)


class requestOfferOtherUser(BrowserView):

    def __call__(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        itemid = self.request.form.get('id')
        portal = api.portal.get()
        currentItem = portal.unrestrictedTraverse(itemid)
        user = api.user.get(userid=self.request.form.get('userRequest'))
        data = getStudentData(self, currentItem, user)
        if data:
            self.request.response.setCookie('APPLICATION_DATA', json.dumps(data), path='/')
            self.request.response.redirect(currentItem.absolute_url() + '/++add++genweb.tfemarket.application')
        else:
            redirectToMarket(self)


class getInfoCreateApplication(BrowserView):

    def __call__(self):
        data = self.request.cookies.pop('APPLICATION_DATA')
        return json.dumps(eval(data))


class getInfoRenameOffer(BrowserView):

    def __call__(self):
        pc = api.portal.get_tool('portal_catalog')
        offer = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                  'UID': self.request.form['UID']})
        if len(offer) > 0:
            offer = offer[0]
            return json.dumps({'title': offer.Title, 'shortname': offer.id})


class resetCountOffers(BrowserView):

    render = ViewPageTemplateFile("views_templates/reset_offers_counter.pt")

    def __call__(self):
        if 'confirm' in self.request.form:
            tfe_tool = genwebTfemarketConfig()
            tfe_tool.count_offers = 0
            transaction.commit()
            self.request.response.redirect(self.context.absolute_url() + "/tfemarket-settings#fieldsetlegend-2")

        return self.render()


class tfemarketUtils(BrowserView):

    def getTFEs(self):
        return getUrlAllTFE(self)

    def canManageTFE(self):
        return checkPermission("genweb.tfemarket.controlpanel", self)

    def isManager(self):
        return checkPermission("genweb.manager", self)


class tfemarketUtilsCopyOffer(BrowserView):

    render = ViewPageTemplateFile("views_templates/tfemarket_utils_copy_offer.pt")

    def getTFEs(self):
        return getUrlAllTFE(self)

    def getOffers(self):
        return getAllOffers(self)

    def __call__(self):
        if 'submit' in self.request.form:
            pc = api.portal.get_tool('portal_catalog')
            offer = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                      'UID': self.request.form['offer']})
            if len(offer) > 0:
                offer = offer[0].getObject()
                market = offer.getParentNode()
                try:
                    data = {
                        'title': 'Copy of ' + offer.title,
                        'description': offer.description,
                        'topic': offer.topic,
                        'offer_type': offer.offer_type if 'offer_type' in offer else _(u'Project'),
                        'degree': offer.degree,
                        'keys': offer.keys,
                        'teacher_manager': offer.teacher_manager,
                        'teacher_fullname': offer.teacher_fullname,
                        'teacher_email': offer.teacher_email,
                        'dept': offer.dept,
                        'type_codirector': offer.type_codirector,
                        'codirector_id': offer.codirector_id,
                        'codirector': offer.codirector,
                        'codirector_email': offer.codirector_email,
                        'codirector_dept': offer.codirector_dept,
                        'num_students': offer.num_students,
                        'workload': offer.workload,
                        'targets': offer.targets,
                        'features': offer.features,
                        'requirements': offer.requirements,
                        'lang': offer.lang,
                        'modality': offer.modality,
                        'company': offer.company,
                        'grant': offer.grant,
                        'confidential': offer.confidential,
                        'environmental_theme': offer.environmental_theme,
                        'scope_cooperation': offer.scope_cooperation,
                        'tfgm': offer.tfgm,
                    }
                    copyOffer = createContentInContainer(market, "genweb.tfemarket.offer", **data)
                    copyOffer.setEffectiveDate(offer.effective_date)
                    copyOffer.setExpirationDate(offer.expiration_date)
                    copyOffer.reindexObject()

                    IStatusMessage(self.request).addStatusMessage(_(u"The offer has been copied."), 'info')
                    self.request.response.redirect(self.context.absolute_url() + "/@@tfemarket-utils-rename-offer?offer=" + copyOffer.UID())
                except:
                    IStatusMessage(self.request).addStatusMessage(_(u"The offer could not be copied."), 'error')
            else:
                IStatusMessage(self.request).addStatusMessage(_(u"The offer could not be copied."), 'error')

        return self.render()


class tfemarketUtilsRenameOffer(BrowserView):

    render = ViewPageTemplateFile("views_templates/tfemarket_utils_rename_offer.pt")

    def getTFEs(self):
        return getUrlAllTFE(self)

    def getOffers(self):
        pc = api.portal.get_tool('portal_catalog')
        filters = {'portal_type': 'genweb.tfemarket.offer',
                   'sort_on': 'sortable_title',
                   'sort_order': 'ascending'}

        roles = api.user.get_current().getRoles()
        if api.user.get_current().id != "admin" and 'TFE Manager' not in roles:
            filters.update({'review_state': ('intranet', 'offered', 'public', 'pending')})

        if 'TFE Teacher' in roles and api.user.get_current().id != "admin":
            filters.update({'Creator': api.user.get_current().id})

        offers = pc.searchResults(**filters)
        res = {'ok': [], 'ko': []}
        for offer in offers:
            data = {'UID': offer.UID,
                    'Title': offer.Title,
                    'offer_id': offer.getObject().offer_id}

            if isManager() or not checkOfferhasApplications(offer.getObject()):
                res['ok'].append(data)
            else:
                res['ko'].append(data)
        return res

    def __call__(self):
        if 'submit' in self.request.form:
            pc = api.portal.get_tool('portal_catalog')
            offer = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                      'UID': self.request.form['offer']})
            if len(offer) > 0:
                offer = offer[0].getObject()
                offer.title = self.request.form['newTitle']
                parent = offer.getParentNode()
                try:
                    parent.manage_renameObject(offer.id, self.request.form['newShortname'])
                    offer.reindexObject()

                    for application in getApplicationsFromContent(offer):
                        application.offer_title = self.request.form['newTitle']
                        application.reindexObject()
                    IStatusMessage(self.request).addStatusMessage(_(u"The offer has been modified."), 'info')
                except:
                    IStatusMessage(self.request).addStatusMessage(_(u"Error the identifier exists."), 'error')
            else:
                IStatusMessage(self.request).addStatusMessage(_(u"Error the identifier exists."), 'error')

        return self.render()


class tfemarketUtilsDeleteOffer(BrowserView):

    render = ViewPageTemplateFile("views_templates/tfemarket_utils_delete_offer.pt")

    def getTFEs(self):
        return getUrlAllTFE(self)

    def getOffers(self):
        pc = api.portal.get_tool('portal_catalog')
        filters = {'portal_type': 'genweb.tfemarket.offer',
                   'review_state': ('intranet', 'offered', 'public', 'pending'),
                   'sort_on': 'sortable_title',
                   'sort_order': 'ascending'}

        if 'TFE Teacher' in api.user.get_current().getRoles() and api.user.get_current().id != "admin":
            filters.update({'Creator': api.user.get_current().id})

        offers = pc.searchResults(**filters)
        res = {'ok': [], 'ko': []}
        for offer in offers:
            data = {'UID': offer.UID,
                    'Title': offer.Title,
                    'offer_id': offer.getObject().offer_id}

            if isManager() or not checkOfferhasApplications(offer.getObject()):
                res['ok'].append(data)
            else:
                res['ko'].append(data)
        return res

    def __call__(self):
        if 'submit' in self.request.form:
            pc = api.portal.get_tool('portal_catalog')
            offer = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                      'UID': self.request.form['offer']})
            if len(offer) > 0:
                offer = offer[0]
                parent = offer.getObject().aq_parent
                try:
                    parent.manage_delObjects([offer.id])
                    IStatusMessage(self.request).addStatusMessage(_(u"The offer has been removed."), 'info')
                except:
                    IStatusMessage(self.request).addStatusMessage(_(u"The offer could not be removed."), 'error')
            else:
                IStatusMessage(self.request).addStatusMessage(_(u"The offer could not be removed."), 'error')

        return self.render()


class tfemarketUtilsStats(BrowserView):

    def getTFEs(self):
        return getUrlAllTFE(self)

    @memoize
    def getStates(self):
        tfe_tool = genwebTfemarketConfig()
        review_state = tfe_tool.review_state

        results = []
        results.append({'id': 'offered', 'lit': 'Proposta'})

        if review_state:
            results.append({'id': 'pending', 'lit': 'En revisió'})

        results.append({'id': 'public', 'lit': 'Pública'})
        results.append({'id': 'intranet', 'lit': 'Intranet'})
        results.append({'id': 'assigned', 'lit': 'Assignada'})
        results.append({'id': 'assignadaintranet', 'lit': 'Assignada (intranet)'})
        results.append({'id': 'registered', 'lit': 'Inscrita'})
        results.append({'id': 'inscritaintranet', 'lit': 'Inscrita (intranet)'})
        results.append({'id': 'expired', 'lit': 'Caducada'})
        return results

    def getDegreesInfo(self):
        pc = api.portal.get_tool('portal_catalog')
        res = []
        for degree in getDegrees():
            if degree['id'] != 'a':
                info = {'id': degree['id'], 'title': degree['lit']}
                for state in self.getStates():
                    data = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                             'TFEdegree': degree['id'],
                                             'review_state': state['id']})
                    info.update({state['id']: len(data)})

                data = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                         'TFEdegree': degree['id']})
                info.update({'total': len(data)})
                res.append(info)

        return res

    def getTotalInfo(self):
        pc = api.portal.get_tool('portal_catalog')
        info = {'title': u"Total"}
        for state in self.getStates():
            data = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                     'review_state': state['id']})
            info.update({state['id']: len(data)})

        data = pc.searchResults({'portal_type': 'genweb.tfemarket.offer'})
        info.update({'total': len(data)})

        return info


class tfemarketUtilsDownloadCSV(BrowserView):

    def getTFEs(self):
        return getUrlAllTFE(self)


class tfemarketUtilsExportCSV(BrowserView):

    def __call__(self):
        if 'UID' in self.request.form:
            wf_tool = getToolByName(self.context, 'portal_workflow')
            tools = getMultiAdapter((self.context, self.request), name='plone_tools')

            output_file = StringIO()
            writer = csv.writer(output_file, delimiter=',')

            pc = api.portal.get_tool('portal_catalog')
            market = pc.searchResults({'portal_type': 'genweb.tfemarket.market',
                                       'UID': self.request.form['UID']})[0]

            if 'submit_offers' in self.request.form:
                tfe_tool = genwebTfemarketConfig()

                if tfe_tool.view_num_students:
                    data_header = ['Offer ID', 'Title', 'Description', 'Topic', 'Type', 'TFG/TFM', 'Degrees', 'Keys',
                                   'Teacher ID', 'Teacher fullname', 'Teacher email', 'Teacher university department',
                                   'Type Codirector', 'Codirector ID', 'Codirector fullname', 'Codirector email',
                                   'Codirector university department', 'Number of students', 'Workload', 'Targets',
                                   'Features', 'Requirements', 'Languages', 'Modality', 'Company', 'Possibility of scholarship',
                                   'Confidential', 'Environmental theme', 'Scope of cooperation',
                                   'Publication date', 'Expiration date', 'Expired', 'State']
                else:  # Omit Num Students
                    data_header = ['Offer ID', 'Title', 'Description', 'Topic', 'Type', 'TFG/TFM', 'Degrees', 'Keys',
                                   'Teacher ID', 'Teacher fullname', 'Teacher email', 'Teacher university department',
                                   'Type Codirector', 'Codirector ID', 'Codirector fullname', 'Codirector email',
                                   'Codirector university department', 'Workload', 'Targets', 'Features',
                                   'Requirements', 'Languages', 'Modality', 'Company', 'Possibility of scholarship',
                                   'Confidential', 'Environmental theme', 'Scope of cooperation',
                                   'Publication date', 'Expiration date', 'Expired', 'State']

                writer.writerow(data_header)

                offers = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                           'path': {"query": market.getPath()}})

                for data in offers:
                    offer = data.getObject()

                    offerWorkflow = tools.workflow().getWorkflowsFor(offer)[0]
                    offerStatus = wf_tool.getStatusOf(offerWorkflow.id, offer)
                    offerState = offerWorkflow['states'][offerStatus['review_state']]

                    expired = offer.expires().isPast()
                    if tfe_tool.view_num_students:
                        writer.writerow([
                            offer.offer_id,
                            offer.title,
                            offer.description,
                            offer.topic if offer.topic else "",
                            offer.offer_type if offer.offer_type else "",
                            '\n'.join(offer.tfgm) if offer.tfgm else "",
                            '\n'.join(offer.degree) if offer.degree else "",
                            '\n'.join(offer.keys) if offer.keys else "",
                            offer.teacher_manager,
                            offer.teacher_fullname,
                            offer.teacher_email,
                            offer.dept,
                            offer.type_codirector if offer.type_codirector else "",
                            offer.codirector_id if offer.codirector_id else "",
                            offer.codirector if offer.codirector else "",
                            offer.codirector_email if offer.codirector_email else "",
                            offer.codirector_dept if offer.codirector_dept else "",
                            offer.num_students or "",
                            offer.workload if offer.workload else "",
                            offer.targets if offer.targets else "",
                            offer.features if offer.features else "",
                            offer.requirements if offer.requirements else "",
                            '\n'.join(offer.lang) if offer.lang else "",
                            offer.modality,
                            offer.company if offer.company else "",
                            'Yes' if offer.grant else 'No',
                            'Yes' if offer.confidential else 'No',
                            'Yes' if offer.environmental_theme else 'No',
                            'Yes' if offer.scope_cooperation else 'No',
                            offer.effective_date.strftime('%d/%m/%Y') if offer.effective_date else "",
                            offer.expiration_date.strftime('%d/%m/%Y') if offer.expiration_date else "",
                            'Yes' if expired else 'No',
                            offerState.title])
                    else:  # Omit Num Students
                        writer.writerow([
                            offer.offer_id,
                            offer.title,
                            offer.description,
                            offer.topic if offer.topic else "",
                            offer.offer_type if offer.offer_type else "",
                            '\n'.join(offer.tfgm) if offer.tfgm else "",
                            '\n'.join(offer.degree) if offer.degree else "",
                            '\n'.join(offer.keys) if offer.keys else "",
                            offer.teacher_manager,
                            offer.teacher_fullname,
                            offer.teacher_email,
                            offer.dept,
                            offer.type_codirector if offer.type_codirector else "",
                            offer.codirector_id if offer.codirector_id else "",
                            offer.codirector if offer.codirector else "",
                            offer.codirector_email if offer.codirector_email else "",
                            offer.codirector_dept if offer.codirector_dept else "",
                            offer.workload if offer.workload else "",
                            offer.targets if offer.targets else "",
                            offer.features if offer.features else "",
                            offer.requirements if offer.requirements else "",
                            '\n'.join(offer.lang) if offer.lang else "",
                            offer.modality,
                            offer.company if offer.company else "",
                            'Yes' if offer.grant else 'No',
                            'Yes' if offer.confidential else 'No',
                            'Yes' if offer.environmental_theme else 'No',
                            'Yes' if offer.scope_cooperation else 'No',
                            offer.effective_date.strftime('%d/%m/%Y') if offer.effective_date else "",
                            offer.expiration_date.strftime('%d/%m/%Y') if offer.expiration_date else "",
                            'Yes' if expired else 'No',
                            offerState.title])

                filename = market.id + "-offers.csv"
            else:
                data_header = ['Offer ID', 'Degree ID', 'DNI', 'Fullname', 'Telephone', 'Email',
                               'PRISMA ID', 'Expedient ID', 'Body', 'State']

                writer.writerow(data_header)

                requests = pc.searchResults({'portal_type': 'genweb.tfemarket.application',
                                             'path': {"query": market.getPath()}})

                for data in requests:
                    app = data.getObject()

                    appWorkflow = tools.workflow().getWorkflowsFor(app)[0]
                    appStatus = wf_tool.getStatusOf(appWorkflow.id, app)
                    appState = appWorkflow['states'][appStatus['review_state']]

                    writer.writerow([
                        app.offer_id,
                        app.degree_id,
                        app.dni,
                        app.title,
                        app.phone if app.phone else "",
                        app.email,
                        app.prisma_id if app.prisma_id else "",
                        app.codi_expedient if app.codi_expedient else "",
                        app.body if app.body else "",
                        appState.title])

                filename = market.id + "-applications.csv"

            self.request.response.setHeader('Content-Type', 'text/csv')
            self.request.response.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)
            return output_file.getvalue()


class tfemarketUtilsRequestOffer(BrowserView):

    render = ViewPageTemplateFile("views_templates/tfemarket_utils_request_offer.pt")

    def getTFEs(self):
        return getUrlAllTFE(self)

    def getOffers(self):
        return getAllOffers(self)

    def __call__(self):
        if 'submit' in self.request.form:
            pc = api.portal.get_tool('portal_catalog')
            offer = pc.searchResults({'portal_type': 'genweb.tfemarket.offer',
                                      'UID': self.request.form['offer']})
            if len(offer) > 0:
                offerObj = offer[0].getObject()
                self.request.response.redirect(offerObj.aq_parent.absolute_url() + '/requestOfferOtherUser?id=' + '/'.join(offerObj.getPhysicalPath()[2:]) + '&offer=' + offerObj.offer_id + '&userRequest=' + self.request.form['userRequest'] + '&open=Y')

        return self.render()


class tfemarketUtilsFixOwnerApplication(BrowserView):

    render = ViewPageTemplateFile("views_templates/tfemarket_utils_fix_owner_application.pt")

    def getTFEs(self):
        return getUrlAllTFE(self)

    def getApplications(self):
        return getAllApplications(self)

    def __call__(self):
        if 'submit' in self.request.form:
            pc = api.portal.get_tool('portal_catalog')
            app = pc.searchResults({'portal_type': 'genweb.tfemarket.application',
                                    'UID': self.request.form['application']})

            if len(app) > 0:
                app = app[0].getObject()
                currentUser = api.user.get_current()
                newUser = self.request.form['userRequest']

                app.manage_delLocalRoles([currentUser])
                app.creators = tuple([newUser])
                app.manage_setLocalRoles(newUser, ["Owner"])
                app.setCreators(newUser)
                app.addCreator(newUser)
                app.reindexObjectSecurity()
                app.reindexObject()
                transaction.commit()

                IStatusMessage(self.request).addStatusMessage(_(u'OK'), 'info')

        return self.render()


def getUrlAllTFE(self):
    pc = api.portal.get_tool('portal_catalog')
    return pc.searchResults({'portal_type': 'genweb.tfemarket.market'})


def getAllOffers(self):
    pc = api.portal.get_tool('portal_catalog')
    filters = {'portal_type': 'genweb.tfemarket.offer',
               'sort_on': 'sortable_title',
               'sort_order': 'ascending'}

    if 'TFE Teacher' in api.user.get_current().getRoles() and api.user.get_current().id != "admin":
        filters.update({'Creator': api.user.get_current().id})

    offers = pc.searchResults(**filters)
    res = []
    for offer in offers:
        res.append({'UID': offer.UID,
                    'Title': offer.Title,
                    'offer_id': offer.getObject().offer_id})
    return res


def getAllApplications(self):
    pc = api.portal.get_tool('portal_catalog')
    filters = {'portal_type': 'genweb.tfemarket.application',
               'sort_on': 'sortable_title',
               'sort_order': 'ascending'}

    applications = pc.searchResults(**filters)
    res = []
    for app in applications:
        offer = app.getObject().aq_parent
        res.append({'UID': app.UID,
                    'Title': app.Title,
                    'offer_id': offer.offer_id,
                    'offer_title': offer.Title})
    return res


def checkOfferhasApplications(offer):
    return len(getApplicationsFromContent(offer)) > 0


class fillEmptyTFGMOffers(BrowserView):

    def getDegreesProgramType(self):
        tfe_tool = genwebTfemarketConfig()

        result = {}
        if tfe_tool.titulacions_table:
            for item in tfe_tool.titulacions_table:
                result.update({item['codi_mec']: item['progam_type']})

        return result

    def __call__(self):
        degrees = self.getDegreesProgramType()

        pc = api.portal.get_tool('portal_catalog')
        offers = pc.searchResults({'portal_type': 'genweb.tfemarket.offer'})
        for data in offers:
            offer = data.getObject()
            if not offer.tfgm:
                tfgm = []
                for degree in offer.degree:
                    if degree in degrees:
                        if degrees[degree] == 'MA' and 'TFM' not in tfgm:
                            tfgm.append('TFM')
                        elif degrees[degree] == 'GR' and 'TFG' not in tfgm:
                            tfgm.append('TFG')
            offer.tfgm = tfgm
            offer.reindexObject()
        return 'Finished'


class changeUPCCodirectorValues(BrowserView):

    def __call__(self):
        pc = api.portal.get_tool('portal_catalog')
        offers = pc.searchResults({'portal_type': 'genweb.tfemarket.offer'})
        result = {}
        for data in offers:
            offer = data.getObject()
            if offer.type_codirector == 'UPC':
                if offer.codirector_id and ' ' in offer.codirector_id:
                    result.update({offer.codirector_id: offer.codirector})
                    codirector_tmp = offer.codirector_id
                    offer.codirector_id = offer.codirector
                    offer.codirector = codirector_tmp
                    offer.reindexObject()
        return json.dumps(result)


class getErrorsKeys(BrowserView):

    def __call__(self):
        pc = api.portal.get_tool('portal_catalog')
        offers = pc.searchResults({'portal_type': 'genweb.tfemarket.offer'})
        listado = []
        for offer in offers:
            offer_obj = offer.getObject()
            if type(offer_obj.keys).__name__ == 'method':
                listado.append(offer_obj.id)

        return json.dumps(listado)

class clearErrorsKeys(BrowserView):

    def __call__(self):
        pc = api.portal.get_tool('portal_catalog')
        offers = pc.searchResults({'portal_type': 'genweb.tfemarket.offer'})
        for offer in offers:
            offer_obj = offer.getObject()
            if type(offer_obj.keys).__name__ == 'method':
                offer_obj.keys = []
                offer_obj.reindexObject()

        transaction.commit()