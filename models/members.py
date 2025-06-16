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

from odoo import fields, models, api,_
from .zksdk import zksdk, Utils
import logging
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class GymMember(models.Model):
    _name = "gym.member"
    _inherit = ["mail.thread", 'mail.activity.mixin']
    _description = "Gym Member"


class MemberPartner(models.Model):
    _inherit = 'res.partner'
    machine_user_ids = fields.One2many('zk.machine.user', 'user_id',string='Machine User ID')
    machine_attendance_ids = fields.One2many('zk.machine.attendance', 'user_id',string='Machine Attendance ID')
    machine_user_id = fields.Integer('Machine User ID', tracking=True, copy=False, default="")
    member_card = fields.Char(string='Card Number',required=False)
    is_member_card_created = fields.Boolean('Member Card Created', default=False)

    # _sql_constraints = [
    #     ('zkpartner_member_card', 'UNIQUE (member_card)', 'Este cartão já foi usado!'),
    # ]

    @api.constrains('member_card')
    def _check_member_card(self):
        if not self.member_card:
            raise ValidationError(_('Please input a card member'))
        else:
            for rec in self:
                domain = [('member_card', '=', rec.member_card)]
                count = self.sudo().search_count(domain)
                if count > 1:
                    raise ValidationError(_("Este cartão já foi usado"))
            self.is_member_card_created = True

    #HH
    def action_upload_member(self,selected_device):
        zk = zksdk(ip=selected_device.machine_id.ip, port="4370",machine_number=1)
        selected_partners = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        users = self.env['zk.machine.user']
        if zk.connectDevice():
            zk.disableDevice()
            for rec in selected_partners:
                if not rec.machine_user_id:
                    rec.write({'machine_user_id': self.env['ir.sequence'].next_by_code('machine.user')})

                m_user_name = rec.name[:8]
                m_user_enable = 0
                if rec.membership_state == "paid":
                    m_user_enable = 1
                else:
                    m_user_enable = 0

                zk.setCardNumber(rec.member_card)
                zk.setUserInfo(rec.machine_user_id, m_user_name,"", 0, m_user_enable)
                get_user_id = self.env['zk.machine.user'].search([('user_id', '=', rec.id)])
                if get_user_id:
                    #update user data in database
                    get_user_id.write({'machine_id': selected_device.machine_id.id,
                                  #'user_id': rec.id,
                                  'user_name': m_user_name,
                                  'user_password': "",
                                  'user_privilege': "0",
                                  'user_is_enable': m_user_enable})

                else:                    
                    users.create({'machine_id': selected_device.machine_id.id,
                                 'user_id': rec.id,
                                 'user_name': m_user_name,
                                 'user_password': "",
                                 'user_privilege': "0",
                                 'user_is_enable': m_user_enable})
            zk.refreshData()
            zk.enableDevice()
            zk.disconnectDevice()
            return Utils.notify('Success','success',"Member created/updated",False)    
        
        else:
            return Utils.notify('Warning','warning',"Cannot connect to device",False)

       
    def action_disable_member(self,selected_device):        
        zk = zksdk(ip=selected_device, port="4370",machine_number=1)
        selected_partners = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        if zk.connectDevice():
            #Teste
            #print(zk.unlockDoor())
            zk.disableDevice()            
            for rec in selected_partners:
                if rec.machine_user_id:
                    zk.enableUser(rec.machine_user_id,0)

            zk.refreshData()
            zk.enableDevice()
            zk.disconnectDevice()
            return Utils.notify('Success', 'success', "Member(s) disabled'", False)

        else:
            return Utils.notify('Warning','warning',"Cannot connect to device",False)

    def action_enable_member(self):
        _logger.info("++++++++++++Enable Member ++++++++++++++++++++++")
        # user = self.env.user
        # if user.has_group('gym_mgmt_system_zk_integration.group_gym_manager'):

            #zk = zksdk(ip="192.168.1.106", port="4370",machine_number=1)
        for rec in self:
            get_machines = self.env['zk.machine.user'].search([('user_id', '=', rec.id)])
            for device in get_machines:
                zk = zksdk(ip=device.machine_id.ip, port=device.machine_id.port_no, machine_number=1)
                if zk.connectDevice():
                      zk.disableDevice()
                      if rec.machine_user_id:
                        zk.enableUser(rec.machine_user_id,1)
                      _logger.info("++++++++++++"+rec.name+ " "+ device.machine_id.name +": Member Enabled ++++++++++++++++++++++")
                      zk.refreshData()
                      zk.enableDevice()
                      zk.disconnectDevice()
    # else:
        #     raise ValidationError(_('Não tem acesso a esta função'))

            #return Utils.notify('Success','success',"Member Enabled on Device",False)

    def automated_action_disable_member(self):
        _logger.info("++++++++++++Disable Member ++++++++++++++++++++++")
        for rec in self:
            get_machines = self.env['zk.machine.user'].search([('user_id', '=', rec.id)])
            for device in get_machines:
                zk = zksdk(ip=device.machine_id.ip, port=device.machine_id.port_no, machine_number=1)
                if zk.connectDevice():
                      zk.disableDevice()
                      if rec.machine_user_id:
                        zk.enableUser(rec.machine_user_id,0)
                      _logger.info("++++++++++++"+rec.name+ " "+ device.machine_id.name +": Member Disabled ++++++++++++++++++++++")
                      zk.refreshData()
                      zk.enableDevice()
                      zk.disconnectDevice()

    def action_open_upload_wizard(self):
        return {
            'name': 'Device Selection',
            'type': 'ir.actions.act_window',
            'res_model': 'device.selection',
            'view_mode': 'form',
            'view_id':self.env.ref('gym_mgmt_system_zk_integration.device_selection_wizard_upload_form_view').id,
            'target': 'new',
            'context': {'default_name': 'Upload Member - Device Selection'},
        }
    
    def action_open_disable_wizard(self):
        return {
            'name': 'Device Selection',
            'type': 'ir.actions.act_window',
            'res_model': 'device.selection',
            'view_mode': 'form',
            'view_id':self.env.ref('gym_mgmt_system_zk_integration.device_selection_wizard_disable_form_view').id,
            'target': 'new',
            'context': {'default_name': 'Disable Member - Device Selection'},
        }

    def action_open_enable_wizard(self):
        return {
            'name': 'Device Selection',
            'type': 'ir.actions.act_window',
            'res_model': 'device.selection',
            'view_mode': 'form',
            'view_id':self.env.ref('gym_mgmt_system_zk_integration.device_selection_wizard_enable_form_view').id,
            'target': 'new',
            'context': {'default_name': 'Disable Member - Device Selection'},
        }

    def action_membership_state(self):
       
            notification_title = _('Member State')
            notification_type = 'success'
            notification_message = _(self.membership_state)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': notification_title,
                    'message': notification_message,
                    'type': notification_type,
                }
            }

#HH
class AttendanceLines(models.Model):
    _name = "gym.attendancelines"
    _description = "Attendance Lines"

    partner_id = fields.Many2one('res.partner', 'AttendanceLines')
    device_id = fields.Integer(string='Biometric Device ID')
    inOutMode = fields.Integer("The attendance status of an attendance record")
    punch_date_time = fields.Date(string='Punch DateTine', help="Date and time of the attendance record.")