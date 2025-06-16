# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: cybrosys(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import pytz
import sys
from datetime import datetime
import logging
import binascii

from odoo import fields, models, api, _
from .zksdk import zksdk, Utils 

from struct import unpack
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
try:
    from .zksdk import zksdk
except ImportError:
    _logger.error("Please Install zksdk library.")


class ZkMachine(models.Model):

    """This module is for the ZK Machine."""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ZK Machine"

    _name = 'zk.machine'
    name = fields.Char(string='Machine Name', required=True)
    ip = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True)    
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    user_ids = fields.One2many('zk.machine.user', 'machine_id', string='Users Ids')
    attendance_ids = fields.One2many('zk.machine.attendance', 'machine_id', string='Attendance Ids')

    def device_connect(self, zk):
        #        try:
        return zk.connectDevice()

    #        except:
    #           return False

    # def clear_attendance(self):
    #     for info in self:
    #         try:
    #             machine_ip = info.name
    #             zk_port = info.port_no
    #             timeout = 30
    #             try:
    #                 zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
    #             except NameError:
    #                 raise UserError(_("Please install it with 'pip3 install pyzk'."))
    #             conn = self.device_connect(zk)
    #             if conn:
    #                 conn.enable_device()
    #                 clear_data = zk.get_attendance()
    #                 if clear_data:
    #                     # conn.clear_attendance()
    #                     self._cr.execute("""delete from zk_machine_attendance""")
    #                     conn.disconnect()
    #                     raise UserError(_('Attendance Records Deleted.'))
    #                 else:
    #                     raise UserError(_('Unable to clear Attendance log. Are you sure attendance log is not empty.'))
    #             else:
    #                 raise UserError(
    #                     _('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))
    #         except:
    #             raise ValidationError(
    #                 'Unable to clear Attendance log. Are you sure attendance device is connected & record is not empty.')

    def download_users(self):
        _logger.info("++++++++++++Cron Executed - Download Users++++++++++++++++++++++")
        #        try:
        users = self.env['zk.machine.user']
        zk = zksdk(ip=self.ip, port=self.port_no, machine_number=1)
        if self.device_connect(zk):
            zk_users = zk.getAllUserInfo()
            zk_changed_users = zk_users[1:len(zk_users)]
            print(zk_users)
            print(zk_changed_users)
            for user in zk_changed_users:
                get_user_id = self.env['zk.machine.user'].search([('partner_mach_user_id', '=', user[1])])
                #o membro existe na tabela, apenas deve-se actualizar o registo
                if get_user_id:
                    #update user data in database
                    get_user_id.write({'machine_id': self.id,
                                 # 'user_id': user[1],
                                  'user_name': user[2],
                                  'user_password': user[3],
                                  'user_privilege': str(user[4]),
                                  'user_is_enable': user[5],
                                  'member_card_number': user[7]})

                #o membro existe na tabela, mas não está associado a qq parceiro, deve-se actualizar o registo
                else:                    
                    get_user_id = self.env['zk.machine.user'].search([('machine_user_id', '=', user[1])])
                           
                    if get_user_id:
                        #update user data in database
                        get_user_id.write({'machine_id': self.id,
                                   # 'machine_user_id': user[1],
                                    'user_name': user[2],
                                    'user_password': user[3],
                                    'user_privilege': str(user[4]),
                                    'user_is_enable': user[5],
                                    'member_card_number': user[7]})

                    #o membro não existe na tabela, mas existe parceiro, deve-se criar o registo na tabela
                    else:   
                        get_partner_id = self.env['res.partner'].search([('machine_user_id', '=', user[1])])

                        if get_partner_id:
                            users.create({'machine_id': self.id,
                                        'user_id': get_partner_id.id,
                                        'user_name': user[2],
                                        'user_password': user[3],
                                        'user_privilege': str(user[4]),
                                        'user_is_enable': user[5],
                                        'member_card_number': user[7]})

                        #o membro não existe na tabela, não existe parceiro, deve-se criar o registo
                        else:
                            users.create({'machine_id': self.id,
                                        'machine_user_id': user[1],
                                        'user_name': user[2],
                                        'user_password': user[3],
                                        'user_privilege': str(user[4]),
                                        'user_is_enable': user[5],
                                        'member_card_number': user[7]})
        else:
            return Utils.notify('Warning','warning',"Cannot connect to device",False)

    def upload_users(self):
        _logger.info("++++++++++++Cron Executed - Upload Users++++++++++++++++++++++")
        zk = zksdk(ip=self.ip, port=self.port_no, machine_number=1)
        if self.device_connect(zk):
            zk.disableDevice()
            get_users = self.env['zk.machine.user'].search([])         
            for user in get_users:                
                print(user)
                if user.partner_mach_user_id:
                    zk.setCardNumber(user.member_card_number)
                    zk.setUserInfo(user.partner_mach_user_id,user.user_name,user.user_password,user.user_privilege,user.user_is_enable)
                else:
                    zk.setUserInfo(user.machine_user_id,user.user_name,user.user_password,user.user_privilege,user.user_is_enable)                
            zk.refreshData()
            zk.enableDevice()
            zk.disconnectDevice()

            return Utils.notify('Success','success','Users Uploaded',False)
        else:
            return Utils.notify('Warning','warning',"Cannot connect to device",False)

    
    def set_time(self):
        zk = zksdk(ip=self.ip, port=self.port_no, machine_number=1)
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        localized_datetime = pytz.utc.localize(datetime.now()).astimezone(local)
        
        if self.device_connect(zk):
            #zk.setDeviceTime()
            zk.setDeviceTime2(localized_datetime.year, localized_datetime.month,localized_datetime.day, localized_datetime.hour, localized_datetime.minute, localized_datetime.second)
            return Utils.notify('Success','success','Time Set: '+datetime.strftime(localized_datetime,"%d/%m/%Y %H:%M%S"),False)
            #print(zk.getSysOption("~ZKFPVersion"))           
        else:
            return Utils.notify('Warning','warning',"Cannot connect to device",False)

    def cron_setTime(self):

        machines = self.env['zk.machine'].search([])    
        for machine in machines:
            zk = zksdk(ip=machine.ip, port=machine.port_no, machine_number=1)                     
            if self.device_connect(zk):
                user_tz = self.env.user.tz or pytz.utc
                local = pytz.timezone(user_tz)
                localized_datetime = pytz.utc.localize(datetime.now()).astimezone(local)
                zk.setDeviceTime2(localized_datetime.year, localized_datetime.month,localized_datetime.day, localized_datetime.hour, localized_datetime.minute, localized_datetime.second)
                _logger.info("++++++++++++Cron Set Device Time: "+machine.name+" Sucess"+"++++++++++++++++++++++")
            else:
                _logger.info("++++++++++++Cron Set Device Time: "+machine.name+" Device Not connected"+"++++++++++++++++++++++")


    def get_time(self):
        zk = zksdk(ip=self.ip, port=self.port_no, machine_number=1)
        if self.device_connect(zk):
           return Utils.notify('Data e Hora','success',zk.getDeviceTime(),True)
        else:
            return Utils.notify('Warning','warning',"Cannot connect to device",False)

    def unlock_door(self):
        zk = zksdk(ip=self.ip, port=self.port_no, machine_number=1)
        if self.device_connect(zk):
            zk.unlockDoor()
            return Utils.notify('Abertura Porta', 'success', "Porta Aberta", False)
        else:
            return Utils.notify('Abertura Porta', 'warning', "Não foi possível abir a porta", False)

    def download_attendance(self):
        _logger.info("++++++++++++Cron Executed - Download Attendance++++++++++++++++++++++")
        attendance = self.env['zk.machine.attendance']
        zk = zksdk(ip=self.ip, port=self.port_no, machine_number=1)
        if self.device_connect(zk):
            zk_attendance = zk.getAllGLogData()
            zk_changed_attendance = zk_attendance[1:len(zk_attendance) - 1]
            print(zk_changed_attendance)
            for attend in zk_changed_attendance:
                enrollnumber = attend[1]
                verify_mode = attend[2]
                inoutmode = attend[3]
                timestr = datetime.strptime(attend[4], '%Y-%m-%d %H:%M:%S')
                atten_time = timestr
                local_tz = pytz.timezone(
                    self.env.user.partner_id.tz or 'GMT')
                local_dt = local_tz.localize(atten_time, is_dst=None)
                utc_dt = local_dt.astimezone(pytz.utc)
                utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                atten_time = datetime.strptime(
                    utc_dt, "%Y-%m-%d %H:%M:%S")
                atten_time = fields.Datetime.to_string(atten_time)

                get_att_id = self.env['zk.machine.attendance'].search([('machine_id', '=', self.id),
                                                                       ('partner_mach_user_id', '=', enrollnumber),
                                                                       ('punching_time', '=', atten_time)])
                if get_att_id:
                    continue
                else:
                    get_partner_id = self.env['res.partner'].search([('machine_user_id', '=', enrollnumber)])
                    attendance.create({'machine_id': self.id,
                                       'user_id': get_partner_id.id,
                                       'punch_type': str(inoutmode),
                                       'attendance_type': str(verify_mode),
                                       'punching_time': atten_time})
        else:
            return Utils.notify('Warning','warning',"Cannot connect to device",False)

    def update_time():
        _logger.info("++++++++++++Cron Executed - Update Time++++++++++++++++++++++")

#     zk_attendance = self.env['zk.machine.attendance']
#     att_obj = self.env['hr.attendance']
#     for info in self:
#         machine_ip = info.name
#         zk_port = info.port_no
#         try:
#             zk = zksdk(ip="192.168.1.106", port="4370")
#             raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
#         conn = zk.connectDevice()
#         if conn:
#             # conn.disable_device() #Device Cannot be used during this time.
#             try:
#                 user = zk.get_users()
#             except:
#                 user = False
#             try:
#                 attendance = zk.get_attendance()
#             except:
#                 attendance = False
#             if attendance:
#                 for each in attendance:
#                     atten_time = each.timestamp
#                     atten_time = datetime.strptime(atten_time.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
#                     local_tz = pytz.timezone(
#                         self.env.user.partner_id.tz or 'GMT')
#                     local_dt = local_tz.localize(atten_time, is_dst=None)
#                     utc_dt = local_dt.astimezone(pytz.utc)
#                     utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
#                     atten_time = datetime.strptime(
#                         utc_dt, "%Y-%m-%d %H:%M:%S")
#                     atten_time = fields.Datetime.to_string(atten_time)
#                     if user:
#                         for uid in user:
#                             if uid.user_id == each.user_id:
#                                 get_user_id = self.env['hr.employee'].search(
#                                     [('device_id', '=', each.user_id)])
#                                 if get_user_id:
#                                     duplicate_atten_ids = zk_attendance.search(
#                                         [('device_id', '=', each.user_id), ('punching_time', '=', atten_time)])
#                                     if duplicate_atten_ids:
#                                         continue
#                                     else:
#                                         zk_attendance.create({'employee_id': get_user_id.id,
#                                                               'device_id': each.user_id,
#                                                               'attendance_type': str(each.status),
#                                                               'punch_type': str(each.punch),
#                                                               'punching_time': atten_time,
#                                                               'address_id': info.address_id.id})
#                                         att_var = att_obj.search([('employee_id', '=', get_user_id.id),
#                                                                   ('check_out', '=', False)])
#                                         print('ddfcd', str(each.status))
#                                         if each.punch == 0: #check-in
#                                             if not att_var:
#                                                 att_obj.create({'employee_id': get_user_id.id,
#                                                                 'check_in': atten_time})
#                                         if each.punch == 1: #check-out
#                                             if len(att_var) == 1:
#                                                 att_var.write({'check_out': atten_time})
#                                             else:
#                                                 att_var1 = att_obj.search([('employee_id', '=', get_user_id.id)])
#                                                 if att_var1:
#                                                     att_var1[-1].write({'check_out': atten_time})
#
#                                 else:
#                                     print('ddfcd', str(each.status))
#                                     print('user', uid.name)
#                                     employee = self.env['hr.employee'].create(
#                                         {'device_id': each.user_id, 'name': uid.name})
#                                     zk_attendance.create({'employee_id': employee.id,
#                                                           'device_id': each.user_id,
#                                                           'attendance_type': str(each.status),
#                                                           'punch_type': str(each.punch),
#                                                           'punching_time': atten_time,
#                                                           'address_id': info.address_id.id})
#                                     att_obj.create({'employee_id': employee.id,
#                                                     'check_in': atten_time})
#                             else:
#                                 pass
#                 # zk.enableDevice()
#                 conn.disconnect
#                 return True
#             else:
#                 raise UserError(_('Unable to get the attendance log, please try again later.'))
#         else:
#             raise UserError(_('Unable to connect, please check the parameters and network connections.'))

class ZkMachineAttendance(models.Model):

    """This module is for the ZK Machine Attendance."""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ZK Machine Attendance"

    _name = 'zk.machine.attendance'
#    _inherit = 'hr.attendance'

    # @api.constrains('check_in', 'check_out', 'employee_id')
    # def _check_validity(self):
    #     """overriding the __check_validity function for employee attendance."""
    #     pass

    machine_id = fields.Many2one('zk.machine', string='Biometric Device ID')
    user_id = fields.Many2one('res.partner', string='Partner ID')
    partner_mach_user_id = fields.Integer(related='user_id.machine_user_id', readonly=False)
    punch_type = fields.Selection([('0', 'Check In'),
                                   ('1', 'Check Out'),
                                   ('2', 'Break Out'),
                                   ('3', 'Break In'),
                                   ('4', 'Overtime In'),
                                   ('5', 'Overtime Out')],
                                  string='Punching Type')

    attendance_type = fields.Selection([('0','FP/PW/RF'),
                                        ('1','Finger'),
                                        ('2','Password'),
                                        ('3','RF'),
                                        ('4','Teste'),
                                        ],
                                        string='Attendance Type')

    punching_time = fields.Datetime(string='Punching Time')
    #address_id = fields.Many2one('res.partner', string='Working Address')

    _order = "punching_time desc"

class ZkMachineUser(models.Model):

    """This module is for the ZK Machine User."""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "ZK Machine User"

    _name = 'zk.machine.user'
#    _inherit = 'hr.attendance'

    machine_user_id = fields.Integer(string='Machine User Id', required=False)
    partner_mach_user_id = fields.Integer(related='user_id.machine_user_id', readonly=False)

    user_id = fields.Many2one('res.partner', string='Partner ID')
    partner_id = fields.Char(compute='_compute_d_name')
    machine_id = fields.Many2one('zk.machine', string='Biometric Device ID')    
    user_name = fields.Char(string='User Name', required=True)    
    user_password = fields.Char(string='User Password', required=False)
    user_privilege = fields.Selection([('0', 'Common User'),
                                        ('1', 'Registrar'),
                                        ('2','Administrator'),
                                        ('3','Super Administrator')],
                                         string='User Privilege')

    user_is_enable = fields.Boolean(string='User enable?')
    #card_number = fields.Char(string='Card Number', required=False)
    member_card_number = fields.Char(related='user_id.member_card', string='Card Number', readonly=False)
    membership_status = fields.Selection('res.partner', related='user_id.membership_state', string="Membership Status", readonly=True)
    _order = "user_id asc"
    _sql_constraints = [
        ('zkuser_user_id_uq', 'UNIQUE (user_id)', 'The field  must be unique!'),
    ]

    @api.depends('user_id')
    def _compute_d_name(self):
        for record in self:
             record.partner_id = str(record.user_id.id)

    def unlink(self):
        _logger.info("++++++++++++Executed - Delete Users++++++++++++++++++++++")
        zk = zksdk(ip=self.machine_id.ip, port=self.machine_id.port_no, machine_number=1)

        if zk.connectDevice():
            zk.disableDevice()
            for rec in self: 
                if rec.partner_mach_user_id:
                    zk.deleteUser(rec.partner_mach_user_id)
                else:
                    zk.deleteUser(rec.machine_user_id)  

            zk.refreshData()
            zk.enableDevice()        
            zk.disconnectDevice()
        return super().unlink()
        _logger.info("++++++++++++User deleted++++++++++++++++++++++")                   

    def upload_users(self):
        print("Uploading Users")
        #today = date.today()
        group_by_machine = self.env['zk.machine.user'].search([]).grouped("machine_id")
        for machine_id, users in group_by_machine.items():
            zk = zksdk(ip=users[0].machine_id.ip, port=users[0].machine_id.port_no, machine_number=1)
            if zk.connectDevice():
               print ("Started Users update on devices")
               zk.disableDevice()
               for user in users:
                   if user.partner_mach_user_id:
                       zk.setCardNumber(user.member_card_number)
                       zk.setUserInfo(user.partner_mach_user_id, user.user_name, user.user_password,
                                      user.user_privilege, user.user_is_enable)
                   else:
                       zk.setUserInfo(user.machine_user_id, user.user_name, user.user_password, user.user_privilege,
                                      user.user_is_enable)

               zk.refreshData()
               zk.enableDevice()
               zk.disconnectDevice()
               print ("Ended Users update on devices")

    def cron_membership_state_management(self):
        _logger.info("++++++++++++Device Update Membership ++++++++++++++++++++++")
        #today = date.today()
        group_by_machine = self.search([]).grouped("machine_id")
        for machine_id, users in group_by_machine.items():
            zk = zksdk(ip=users[0].machine_id.ip, port=users[0].machine_id.port_no, machine_number=1)
            if zk.connectDevice():
               print ("Started membership update on devices")
               zk.disableDevice()
               for machine_user in users:
                    if machine_user.partner_mach_user_id != 1 and machine_user.partner_mach_user_id != 2\
                            and machine_user.partner_mach_user_id != 21:
                        if machine_user.membership_status == "paid":
                            zk.enableUser(machine_user.partner_mach_user_id,1)
                            machine_user.user_is_enable = True
                        else:
                            zk.enableUser(machine_user.partner_mach_user_id,0)
                            machine_user.user_is_enable = False
               zk.refreshData()
               zk.enableDevice()
               zk.disconnectDevice()
               print ("Ended membership update on devices")



