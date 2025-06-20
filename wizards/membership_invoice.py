# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date, timedelta


class MembershipInvoice(models.TransientModel):
    _inherit = 'membership.invoice'

    membership_date_from = fields.Date(related='product_id.product_tmpl_id.membership_date_from', string='Mem Start Date',
                                       readonly=False)

    membership_date_to = fields.Date(related='product_id.product_tmpl_id.membership_date_to', string='Mem End Date',
                                     readonly=True)

    # product_id = fields.Many2one('product.product', string='Membership', required=True)
    # member_price = fields.Float(string='Member Price', digits='Product Price', required=True)
    #
    @api.onchange('product_id')
    def onchange_product(self):
        """This function returns value of  product's member price based on product id.
        """
        # price_dict = self.product_id._price_compute('list_price')
        # self.member_price = price_dict.get(self.product_id.id) or False
        super().onchange_product()
        self.product_id.product_tmpl_id.membership_date_from = fields.Date.today()
        self.product_id.product_tmpl_id.membership_date_to = fields.Date.today() + timedelta(days=30)

    @api.onchange('membership_date_from')
    def onchange_membership_date_from(self):
        if self.product_id:
            self.product_id.product_tmpl_id.membership_date_from = self.membership_date_from
            self.membership_date_to = self.membership_date_from + timedelta(days=30)
            self.product_id.product_tmpl_id.membership_date_to = self.membership_date_from + timedelta(days=30)

# def membership_invoice(self):
    #     invoice_list = self.env['res.partner'].browse(self._context.get('active_ids')).create_membership_invoice(self.product_id, self.member_price)
    #
    #     search_view_ref = self.env.ref('account.view_account_invoice_filter', False)
    #     form_view_ref = self.env.ref('account.view_move_form', False)
    #     tree_view_ref = self.env.ref('account.view_move_tree', False)
    #
    #     return  {
    #         'domain': [('id', 'in', invoice_list.ids)],
    #         'name': 'Membership Invoices',
    #         'res_model': 'account.move',
    #         'type': 'ir.actions.act_window',
    #         'views': [(tree_view_ref.id, 'tree'), (form_view_ref.id, 'form')],
    #         'search_view_id': search_view_ref and [search_view_ref.id],
    #     }
