
from odoo import http
import logging
_logger = logging.getLogger(__name__)
from odoo.http import request
import werkzeug
import requests
from odoo.addons.web.controllers.main import db_monodb, ensure_db, set_cookie_and_redirect, login_and_redirect
from odoo import registry as registry_get
from odoo import api, http, SUPERUSER_ID, _
import odoo.addons.web.controllers.main as main
import odoo


class Home(main.Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            # csrf_token=request.params['csrf_token']
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            print values
            if uid is not False:
                with registry_get(request.session.db).cursor() as cr:
                    env = api.Environment(cr, SUPERUSER_ID, {})
                    getUserBrowse = env['res.users'].sudo().browse(uid)
                    otp_status = getUserBrowse[0].otp_status
                    # otp_status=False
                    if otp_status:
                            # logout = request.session.logout(keep_db=False)
                            logout = request.session.logout(keep_db=True)
                            request.session['loginKey'] = kw['password']
                            request.session['user_identity'] = uid
                            values['uid'] = uid
                            # values['csrf_token'] = request.csrf_token()
                            return request.render('qlk_authenticator.qlk_otp_confirmation_template', values)
                    # else:
                    #     values['error'] = _(
                    #                 "You may have enabled two factor authentication using App Authenticator. Please contact your Administrator!")
                    #     return request.render('web.login', values)

                request.params['login_success'] = True
                if not redirect:
                    redirect = '/web'
                return http.redirect_with_hash(redirect)
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        return request.render('web.login', values)

    @http.route('/verify/login', auth="public", csrf=False, methods=['POST'])
    def qlk_otp_verify_login(self, *args, **kw):
        ensure_db()
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            user_obj = http.request.env['res.users']
            credentials = user_obj.opt_authenticate({'uid': request.params['uid'],'otp': request.params['otp']})
            if credentials:
                return login_and_redirect(*credentials, redirect_url='/web')
            else:
                logout = request.session.logout(keep_db=True)
                # values = request.params.copy()
                # print values
                # print "*****5"
                values['error'] = _(
                    "One Time Password is Incorrect!")
                return werkzeug.utils.redirect('/web/login')
                # return request.render('qlk_authenticator.qlk_otp_confirmation_template', values)

        else:
            return werkzeug.utils.redirect('/web/login')






