# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.utils import get_installer

import logging

logger = logging.getLogger(__name__)


def upgrade_by_reinstall(context):
    qi = get_installer(context)
    qi.uninstall_product("genweb6.tfemarket")
    qi.install_product("genweb6.tfemarket")