# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Shahul Faiz (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models, _
from datetime import date, timedelta

from .zksdk import zksdk

class MembershipLine(models.Model):
    _inherit = 'membership.membership_line'
    _description = 'Membership Line'
   
    # def change_dates(self):

    #     for rec in self:
    #         rec.date_from = fields.Date.today() 
    #         rec.date_to = fields.Date.today() + timedelta(days=30)
        
    #         notification_title = _('Success')
    #         notification_type = 'success'
    #         notification_message = _('Dates Changed')
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'title': notification_title,
    #                 'message': notification_message,
    #                 'type': notification_type,
    #             }
    #         }