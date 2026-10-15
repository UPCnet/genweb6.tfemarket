# -*- coding: utf-8 -*-
"""Los campos title/description propios llevan max_length (plone.app.dexterity 3.2.3)."""
import importlib
import unittest
import z3c.form.browser.select  # noqa: F401 (los esquemas lo referencian al importarse)
import z3c.form.browser.radio  # noqa: F401
import z3c.form.browser.checkbox  # noqa: F401

try:
    from plone.app.dexterity.config import MAX_DESCRIPTION_LENGTH
    from plone.app.dexterity.config import MAX_TITLE_LENGTH
except ImportError:  # plone.app.dexterity < 3.2.3
    MAX_TITLE_LENGTH = 1024
    MAX_DESCRIPTION_LENGTH = 10000

CASES = [
    ('genweb6.tfemarket.content.offer.offer', 'IOffer', ['title', 'description']),
    ('genweb6.tfemarket.content.application.application', 'IApplication', ['title']),
]


class TestMaxLength(unittest.TestCase):

    def test_title_and_description_have_max_length(self):
        for module, interface, fields in CASES:
            schema = getattr(importlib.import_module(module), interface)
            for name in fields:
                expected = MAX_TITLE_LENGTH if name == 'title' else MAX_DESCRIPTION_LENGTH
                with self.subTest(interface=interface, field=name):
                    self.assertEqual(schema[name].max_length, expected)

    def test_a_longer_value_is_rejected(self):
        from zope.schema.interfaces import TooLong
        module, interface, fields = CASES[0]
        schema = getattr(importlib.import_module(module), interface)
        field = schema[fields[0]]
        limit = MAX_TITLE_LENGTH if fields[0] == 'title' else MAX_DESCRIPTION_LENGTH
        field.bind(None).validate('x' * limit)
        with self.assertRaises(TooLong):
            field.bind(None).validate('x' * (limit + 1))
