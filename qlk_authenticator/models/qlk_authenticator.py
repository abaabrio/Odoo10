# -*- coding: utf-8 -*-

from odoo import models, fields, api

from odoo import _
from odoo.exceptions import Warning

class ResUsers(models.Model):

    _name = 'qlk.authenticator'

    name = fields.Char(string="App Authenticator For", required=False,default=lambda self: self.env.user.name )
    email = fields.Char(string="Email", required=False, )
    company = fields.Char(string="Company", required=False, )
    company_email = fields.Char(string="Company Email", required=False, )
    base32_secret_key = fields.Char(string="Secret Key", required=False, readonly=True,)
    otp_status = fields.Boolean(string="Enable One Time Passwords Login",readonly=True,)
    current_otp = fields.Char(string="Current OTP",readonly=True, )
    qr_otp = fields.Binary(string="QR To Scan",readonly=True, )
    retry_limit = fields.Integer(string="Retry Limit", required=False,default=0,readonly=True, )



    @api.onchange('name')
    def _init_user(self):
        user = self.env['res.users'].search([('id','=',self.env.uid)],)
        print user
        if user.base32_secret_key :
            self.otp_status=user.otp_status
            self.qr_otp=user.qr_otp
            self.base32_secret_key=user.base32_secret_key
            self.current_otp=user.current_otp
            self.retry_limit=user.retry_limit
        else:
            raise Warning(_('Contact Your Administrator to Activate your APP AUTH CODE'))
