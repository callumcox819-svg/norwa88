"""Маршрутизация HTML-шаблонов по сервису GAG (Finn.no / HTMLno)."""

from __future__ import annotations

import unittest

from services.aqua_keys import aqua_service_for_html_dir as gag_service_for_html_dir
from services.html_templates import (
    BACK_FILENAME,
    GO_FILENAME,
    html_subdir_for_service,
    html_template_path,
)


class GagHtmlRoutingTest(unittest.TestCase):
    def test_finn_maps_to_finn_no_folder(self) -> None:
        self.assertEqual(gag_service_for_html_dir("finn_no"), "finn_no")
        self.assertEqual(gag_service_for_html_dir("finn.no"), "finn_no")

    def test_go_back_exist_for_finn(self) -> None:
        svc = "finn_no"
        go = html_template_path(svc, GO_FILENAME)
        back = html_template_path(svc, BACK_FILENAME)
        self.assertIsNotNone(go, "GO missing for finn_no")
        self.assertIsNotNone(back, "BACK missing for finn_no")
        sub = html_subdir_for_service(svc)
        self.assertEqual(sub, "finn_no")
        self.assertIn("finn_no", str(go))
        self.assertIn("finn_no", str(back))

    def test_unknown_service_no_path(self) -> None:
        self.assertIsNone(html_template_path("", GO_FILENAME))
        self.assertIsNone(html_template_path("ebay_de", GO_FILENAME))


if __name__ == "__main__":
    unittest.main()
