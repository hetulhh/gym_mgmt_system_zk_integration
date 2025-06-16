
from odoo import fields, models, api
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    """Inherited the model product Template for adding a field."""
    _inherit = 'product.template'
    
    @api.constrains('membership_date_from')
    def _check_date_from(self):

        for rec in self:
            if rec.membership_date_from < fields.Date.today():
                    raise ValidationError('From date must be greater or equal than today.')
