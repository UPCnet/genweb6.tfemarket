# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from zope.interface import implementer

from genweb6.tfemarket.content.application.application import IApplication
from genweb6.tfemarket.content.market.market import IMarket
from genweb6.tfemarket.content.offer.offer import IOffer


@implementer(IApplication)
class Application(Item):
    pass


@implementer(IMarket)
class Market(Container):
    pass


@implementer(IOffer)
class Offer(Container):
    pass
