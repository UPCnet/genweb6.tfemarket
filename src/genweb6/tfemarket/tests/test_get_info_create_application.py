# -*- coding: utf-8 -*-
"""getInfoCreateApplication no debe evaluar la cookie como codigo Python.

Test unitario (sin capa de Plone): la vista solo lee request.cookies.
"""
from genweb6.tfemarket.browser.views import getInfoCreateApplication

import json
import os
import tempfile
import unittest


class FakeRequest(object):

    def __init__(self, cookies):
        self.cookies = dict(cookies)


class TestGetInfoCreateApplication(unittest.TestCase):

    def _call(self, cookie):
        cookies = {} if cookie is None else {'APPLICATION_DATA': cookie}
        view = getInfoCreateApplication(None, FakeRequest(cookies))
        return json.loads(view())

    def test_valid_json_cookie(self):
        data = {'offer_id': 'o1', 'fullname': 'Ana', 'phone': None}
        self.assertEqual(self._call(json.dumps(data)), data)

    def test_python_code_is_not_executed(self):
        marker = os.path.join(tempfile.gettempdir(), 'genweb6_tfemarket_eval_test')
        if os.path.exists(marker):
            os.remove(marker)
        payload = "__import__('os').system('touch %s')" % marker
        self.assertIsNone(self._call(payload))
        self.assertFalse(os.path.exists(marker))

    def test_python_literal_that_is_not_json(self):
        # eval() lo aceptaba; ahora se rechaza
        self.assertIsNone(self._call("{'a': 1}"))

    def test_missing_cookie(self):
        self.assertIsNone(self._call(None))
