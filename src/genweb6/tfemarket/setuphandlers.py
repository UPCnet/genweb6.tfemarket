# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.LDAPUserFolder.LDAPUserFolder import LDAPUserFolder

from zope.component.hooks import getSite
from zope.interface import implementer

import logging

PROFILE_ID = 'profile-genweb6.tfemarket:default'

INDEXES = (('TFEoffer_id', 'FieldIndex'),
           ('TFEoffer_type', 'FieldIndex'),
           ('TFEtfgm', 'KeywordIndex'),
           ('TFEtopic', 'FieldIndex'),
           ('TFEdegree', 'KeywordIndex'),
           ('TFEteacher_manager', 'FieldIndex'),
           ('TFEdept', 'FieldIndex'),
           ('TFEcompany', 'FieldIndex'),
           ('TFEmodality', 'FieldIndex'),
           ('TFElang', 'KeywordIndex'),
           ('TFEkeys', 'KeywordIndex'),
           ('TFEgrant', 'BooleanIndex'))


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "genweb6.tfemarket:uninstall",
        ]

    def getNonInstallableProducts(self):
        """Hide the upgrades package from site-creation and quickinstaller."""
        return ["genweb6.tfemarket.upgrades"]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
    portal = getSite()

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['sn1'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['sn2'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['givenName'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['unit'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['unitCode'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['segmentation'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['typology'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['DNIpassport'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['idorigen'], REQUEST=None)

    LDAPUserFolder.manage_deleteLDAPSchemaItems(
        portal.acl_users.ldapUPC.acl_users, ldap_names=['mail'], REQUEST=None)


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:

    When called from the import_various method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger(__name__)

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.  Note that
    # this silently does nothing when there is no catalog.xml, so it
    # is quite safe.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()

    indexables = []
    for name, meta_type in INDEXES:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info('Added %s for field %s.', meta_type, name)
    if len(indexables) > 0:
        logger.info('Indexing new indexes %s.', ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)


def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.
    if context.readDataFile('genweb6.tfemarket_various.txt') is None:
        return

    portal = context.getSite()
    logger = logging.getLogger(__name__)
    add_catalog_indexes(portal, logger)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='sn1', friendly_name='Surname 1',
        public_name='sn1', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='sn2', friendly_name='Surname 2',
        public_name='sn2', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='givenName', friendly_name='Name',
        public_name='givenName', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='unit', friendly_name='Unit',
        public_name='unit', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='unitCode', friendly_name='Unit Code',
        public_name='unitCode', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='segmentation', friendly_name='Segmentation',
        public_name='segmentation', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='typology', friendly_name='Typology',
        public_name='typology', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='DNIpassport', friendly_name='DNI',
        public_name='DNIpassport', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='idorigen', friendly_name='Identifier',
        public_name='Identifier', multivalued=True)

    LDAPUserFolder.manage_addLDAPSchemaItem(
        portal.acl_users.ldapUPC.acl_users, ldap_name='mail', friendly_name='eMail',
        public_name='mail', multivalued=False)
