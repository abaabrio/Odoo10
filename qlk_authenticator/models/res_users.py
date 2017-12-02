# -*- coding: utf-8 -*-

from odoo import models, fields, api
import pyotp
import qrcode
import tempfile
import base64
import io, StringIO

from odoo.http import request
from odoo import http, SUPERUSER_ID, _
from odoo import registry as registry_get



class ResUsers(models.Model):
    _inherit = 'res.users'
    _name = 'res.users'
    base32_secret_key = fields.Char(string="Secret Key", required=False)
    otp_status = fields.Boolean(string="Enable One Time Passwords Login")
    current_otp = fields.Char(string="Current OTP", compute="get_actual_otp")
    qr_otp = fields.Binary(string="QR To Scan", compute="generate_qr_code")
    retry_limit = fields.Integer(string="Retry Limit", required=False,default=0 )

    #@api.multi
    def send_mail_authenticator(self,data):
        #for rec in data:
        #    print rec
            # Find the e-mail template
            template = self.env.ref('qlk_authenticator.qlk_authenticator_email_template')
            # You can also find the e-mail template like this:
            # template = self.env['ir.model.data'].get_object('mail_template_demo', 'example_email_template')

            # Send out the e-mail template to the user
            self.env['mail.template'].browse(template.id).send_mail(data.id,raise_exception=False, force_send=True)

    # @api.model
    def generate_secret_key(self):
        for rec in self:
            sk = pyotp.random_base32()
            rec.base32_secret_key = sk
            rec.otp_status=1
            qr_gen=self.generate_qr_code()
            print "Sending email"
            auth_user = self.env['qlk.authenticator'].create(
                {'name': rec.name, 'email': rec.email, 'company': rec.company_id.name,
                 'company_email': rec.company_id.email, 'base32_secret_key': rec.base32_secret_key,
                 'qr_otp': qr_gen, })
            #print qr_gen
            # rec.qr_otp.encode('base64')
            rec.send_mail_authenticator(auth_user)


    def rest_retry_limit(self):
        for rec in self:
            rec.retry_limit=0

    def get_actual_otp(self):
        for rec in self:
            if rec.base32_secret_key :
                totp = pyotp.TOTP(rec.base32_secret_key)
                now_otp = totp.now()
                rec.current_otp = now_otp

    def generate_qr_code(self):
        for rec in self:
            if rec.base32_secret_key :
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                # unicode not decoded
                otp_data = pyotp.totp.TOTP(rec.base32_secret_key).provisioning_uri(rec.company_id.name+"-"+rec.name, issuer_name=rec.email)
                qr.add_data(otp_data)
                qr.make(fit=True)
                qr_pic = qr.make_image()
                f = tempfile.TemporaryFile(mode="r+")
                qr_pic.save(f, 'png')
                f.seek(0)
                qr_pic1 = base64.encodestring(f.read())
                rec.qr_otp = qr_pic1
                # rec.send_mail_authenticator(rec)
                return qr_pic1

    def opt_authenticate(self, data):
        uid = data['uid']
        otp = data['otp']
        dbname = request.session.db
        key = request.session.user_identity
        loginkey = request.session.loginKey
        user_ids = self.env['res.users'].sudo().search([("id", "=", uid)])
        if not user_ids:
            return False
        else:
            for userData in user_ids:
                # userData.retry_limit = userData.retry_limit + 1
                if userData.retry_limit >3 and uid != "1" :
                    del request.session['loginKey']
                    return False
                if str(key) == uid:
                    totp = pyotp.TOTP(userData.base32_secret_key)
                    now_otp = totp.now()
                    # print now_otp
                    if otp == now_otp:
                        # userData.retry_limit = 0
                        del request.session['loginKey']
                        return (dbname, userData.login, loginkey)
                    else:
                        return False



