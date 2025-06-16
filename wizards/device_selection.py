from odoo import api, Command, fields, models

class DeviceSelection(models.TransientModel):
    _name = 'device.selection'
    _description = 'Available Devices'

    machine_id = fields.Many2one('zk.machine', string='Biometric Device ID')

    def action_wizard_upload_member(self):
        my_model = self.env['res.partner']
        return my_model.action_upload_member(self)

    def action_wizard_disable_member(self):
        my_model = self.env['res.partner']
        return my_model.action_disable_member(self.machine_id.ip)

    # def action_wizard_enable_member(self):
    #     my_model = self.env['res.partner']
    #     return my_model.action_enable_member(self.machine_id.ip)