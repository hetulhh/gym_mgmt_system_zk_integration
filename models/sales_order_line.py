from odoo import fields, models, api,_
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'

    membership_date_from = fields.Date(related='product_template_id.membership_date_from',string='Mem Start Date',
                                       readonly=False)

    membership_date_to = fields.Date(related='product_template_id.membership_date_to',string='Mem End Date',
                                     readonly=False)

    is_gym_product = fields.Boolean(related='product_template_id.is_gym_product',string='Is gym product', readonly=False)

    #product_template_id