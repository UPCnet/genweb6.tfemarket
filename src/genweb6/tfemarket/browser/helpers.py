# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone import api
from plone.app.event.base import dt_end_of_day
from plone.app.event.base import dt_start_of_day
from plone.dexterity.utils import createContentInContainer

from genweb6.tfemarket.content.market.market import IMarket
from genweb6.tfemarket.controlpanels.tfemarket import ITfemarketSettings
from genweb6.tfemarket.utils import genwebTfemarketConfig
from genweb6.tfemarket.utils import getExactUserData

import csv
import datetime
import transaction


class importTitulacions(BrowserView):
    """ Import Titulacions from csv file """

    render = ViewPageTemplateFile("helpers_templates/import_titulacions.pt")

    def __call__(self):
        if self.request.environ['REQUEST_METHOD'] == 'POST':
            fitxer = self.request.form['degreesfile']
            filename = fitxer.filename

            if filename != '' and filename.endswith('.csv'):
                tfe_tool = genwebTfemarketConfig()
                tfe_tool.titulacions_table = []

                ifile = open(fitxer, "rb")
                csv_file = csv.reader(ifile, delimiter=',', quotechar='"')
                next(csv_file)  # Ignore header for csv

                for row in csv_file:

                    codi_centre = int(row[0].decode("utf-8"))
                    if not codi_centre == tfe_tool.center_code:
                        continue

                    data = {
                        'codi_prisma': int(row[1].decode("utf-8")),
                        'progam_type': row[2].decode("utf-8"),
                        'codi_mec': row[3].decode("utf-8"),
                        'plan_year': int(row[4].decode("utf-8")),
                        'titulacio_es': row[6].decode("utf-8"),
                        'titulacio_ca': row[5].decode("utf-8"),
                        'titulacio_en': row[7].decode("utf-8"),
                    }

                    tfe_tool.titulacions_table.append(data)

                transaction.commit()
                self.request.response.redirect(self.context.absolute_url() + "/tfemarket-settings#fieldsetlegend-1")
                return
            else:
                message = (u"Falta afegir el fitxer csv.")
                IStatusMessage(self.request).addStatusMessage(message, type='error')

        return self.render()


class importOfertes(BrowserView):
    """ Import Titulacions from csv file """

    render = ViewPageTemplateFile("helpers_templates/import_ofertes.pt")

    def __call__(self):
        if self.request.environ['REQUEST_METHOD'] == 'POST':
            marketUID = self.request.form['market']
            fitxer = self.request.form['offersfile']
            filename = fitxer.filename
            hasHeaders = 'csv_headers' in self.request.form

            if filename != '' and filename.endswith('.csv'):
                msgError = self.createOffers(hasHeaders, fitxer, marketUID)
                if msgError != []:
                    IStatusMessage(self.request).addStatusMessage('\n'.join(msgError), type='error')
                else:
                    self.request.response.redirect(self.context.absolute_url() + "/tfemarket-settings#fieldsetlegend-2")
                    return
            else:
                message = (u"Falta afegir el fitxer csv.")
                IStatusMessage(self.request).addStatusMessage(message, type='alert')

        return self.render()

    def createOffers(self, hasHeaders, fitxer, marketUID):
        tfe_tool = genwebTfemarketConfig()

        catalog = api.portal.get_tool(name='portal_catalog')
        market = catalog(UID=marketUID)[0].getObject()

        msgError = []
        ifile = open(fitxer, "rb")
        csv_file = csv.reader(ifile, delimiter=',', quotechar='"')

        if hasHeaders:
            next(csv_file)  # Ignore header for csv

        for count, row in enumerate(csv_file):
            # Importa ofertas
            notValidDegrees = self.checkNotValidDegrees(row[5].decode("utf-8").split(","))
            if len(notValidDegrees) == 0:
                teacher = getExactUserData(row[7].decode("utf-8"))
                if teacher:
                    teacherDept = teacher['uePerfil'][0]['ueId'] + '-' + teacher['uePerfil'][0]['ueAcronim']
                    for perfil in teacher['uePerfil']:
                        if 'PDI' in perfil['perfilId']:
                            teacherDept = perfil['ueId'] + '-' + perfil['ueAcronim']
                    
                    if 'sobrenom' in teacher:
                        if 'cognom2' in teacher:
                            teacherFullname = f"{teacher['cognom1'].capitalize()} {teacher['cognom2'].capitalize()}, {teacher['sobrenom'].capitalize()}"
                        else:
                            teacherFullname = f"{teacher['cognom1'].capitalize()}, {teacher['sobrenom'].capitalize()}"
                    else:
                        if 'cognom2' in teacher:
                            teacherFullname = f"{teacher['cognom1'].capitalize()} {teacher['cognom2'].capitalize()}, {teacher['nom'].capitalize()}"
                        else:
                            teacherFullname = f"{teacher['cognom1'].capitalize()}, {teacher['nom'].capitalize()}"
                    
                    data = {
                        'title': row[0].decode("utf-8"),
                        'description': row[1].decode("utf-8"),
                        'topic': row[2].decode("utf-8"),
                        'offer_type': row[3].decode("utf-8"),
                        'tfgm': row[4].decode("utf-8").split(","),
                        'degree': row[5].decode("utf-8").split(","),
                        'keys': row[6].decode("utf-8").split(","),
                        'teacher_manager': teacher['commonName'],
                        'teacher_fullname': teacherFullname,
                        'teacher_email': teacher['emailPreferent'],
                        'dept': teacherDept,
                        'num_students': int(row[10].decode("utf-8")),
                        'workload': row[11].decode("utf-8"),
                        'targets': row[12].decode("utf-8"),
                        'features': row[13].decode("utf-8"),
                        'requirements': row[14].decode("utf-8"),
                        'lang': row[15].decode("utf-8").split(","),
                        'modality': row[16].decode("utf-8"),
                        'company': row[17].decode("utf-8"),
                        'grant': bool(row[18].decode("utf-8") == "True"),
                        'confidential': bool(row[19].decode("utf-8") == "True"),
                        'environmental_theme': bool(row[20].decode("utf-8") == "True"),
                        'scope_cooperation': bool(row[21].decode("utf-8") == "True"),
                    }

                    type_codirector = row[8].decode("utf-8")
                    data.update({'type_codirector': type_codirector})
                    if type_codirector == 'UPC':
                        codirector = getExactUserData(row[9].decode("utf-8"))
                        if codirector:
                            codirectorDept = codirector['uePerfil'][0]['ueId'] + '-' + codirector['uePerfil'][0]['ueAcronim']
                            for perfil in codirector['uePerfil']:
                                if 'PDI' in perfil['perfilId']:
                                    codirectorDept = perfil['ueId'] + '-' + perfil['ueAcronim']
                            
                            if 'sobrenom' in codirector:
                                if 'cognom2' in codirector:
                                    codirectorFullname = f"{codirector['cognom1'].capitalize()} {codirector['cognom2'].capitalize()}, {codirector['sobrenom'].capitalize()}"
                                else:
                                    codirectorFullname = f"{codirector['cognom1'].capitalize()}, {codirector['sobrenom'].capitalize()}"
                            else:
                                if 'cognom2' in codirector:
                                    codirectorFullname = f"{codirector['cognom1'].capitalize()} {codirector['cognom2'].capitalize()}, {codirector['nom'].capitalize()}"
                                else:
                                    codirectorFullname = f"{codirector['cognom1'].capitalize()}, {codirector['nom'].capitalize()}"
                            
                            data.update({
                                'codirector_id': codirector['commonName'],
                                'codirector': codirectorFullname,
                                'codirector_email': codirector['emailPreferent'],
                                'codirector_dept': codirectorDept
                            })
                        else:
                            msg = row[0].decode("utf-8") + " - Codirector (" + row[9].decode("utf-8") + ") not exist."
                            print(str(count + 1) + ": Error - " + msg)
                            msgError.append(str(count + 1) + ": " + msg)
                            continue
                    else:
                        data.update({'codirector': row[9].decode("utf-8")})

                    offer = createContentInContainer(market, "genweb.tfemarket.offer", **data)
                    offer.setEffectiveDate(dt_start_of_day(datetime.datetime.today() + datetime.timedelta(1)))
                    offer.setExpirationDate(dt_end_of_day(datetime.datetime.today() + datetime.timedelta(365)))
                    offer.reindexObject()

                    # Importa topics y tags
                    strTopics = row[2].decode("utf-8") + ","
                    topics = list(dict.fromkeys(strTopics.split(",")[:-1]))
                    actualTopics = tfe_tool.topics.split('\r\n')
                    newTopics = "\r\n".join([topic for topic in topics if topic not in actualTopics])
                    if newTopics:
                        tfe_tool.topics += "\r\n" + newTopics.strip()

                    strTags = row[6].decode("utf-8") + ","
                    tags = list(dict.fromkeys(strTags.split(",")[:-1]))
                    actualTags = tfe_tool.tags.split('\r\n')
                    newTags = "\r\n".join([tag for tag in tags if tag not in actualTags])
                    if newTags:
                        tfe_tool.tags += "\r\n" + newTags.strip()

                    transaction.commit()

                    print(str(count + 1) + ": Done - " + row[0].decode("utf-8"))
                else:
                    msg = row[0].decode("utf-8") + " - Teacher (" + row[7].decode("utf-8") + ") not exist."
                    print(str(count + 1) + ": Error - " + msg)
                    msgError.append(str(count + 1) + ": " + msg)
            else:
                msg = row[0].decode("utf-8") + " - Degree (" + " - ".join(notValidDegrees) + ") not valid."
                print(str(count + 1) + ": Error - " + msg)
                msgError.append(str(count + 1) + ": " + msg)

        return msgError

    def getMarkets(self):
        markets = []
        catalog = api.portal.get_tool(name='portal_catalog')
        values = catalog(path={'query': '/'},
                         object_provides=IMarket.__identifier__)
        for market in values:
            markets.append({'value': market.UID, 'title': market.Title})

        return markets

    def checkNotValidDegrees(self, degrees):
        tfe_tool = genwebTfemarketConfig()
        allDegrees = [x['codi_mec'] for x in tfe_tool.titulacions_table]
        notValid = [x for x in degrees if x not in allDegrees]
        return notValid
