# Copyright 2020-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

class PortalContract(CustomerPortal):
    @http.route(
        ["/my/contract/test"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_contract_detail(self):
        return "Teste"
