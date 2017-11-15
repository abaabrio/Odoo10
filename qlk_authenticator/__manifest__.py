# -*- coding: utf-8 -*-
{
    'name': "QLK Authenticator",

    'summary': """
            Two Factor authentication to authenticate user via OTP.
       """,

    'description': """
            To Install The external Dependencies, type in your terminal :
            > pip install pyotp
            > pip install qrcode

    """,
    'author': "Abaab Riadh",
    'website': "http://www.qlinksoftware.com",
    'license': 'OPL-1',
    'version': '1.0',
    'application': True,
    'category': 'System',
    "sequence": 1,
    'depends' : ['base','base_setup','web','mail','contacts'

                 ],
    'images': ['images/main_1.png'],
    'external_dependencies': {
            'python': [
                'pyotp',
                'qrcode',
            ],
            'bin': [],
        },
    'data': [
        # security
        'security/access_rules.xml',
        'security/ir.model.access.csv',

        # Default Data
        'views/view/qlk_res_user_form.xml',
        'views/view/web_otp_template.xml',
        'views/view/qlk_authenticator_view.xml',
        'views/menu/qlk_authenticator_menu.xml',
        'data/qlk_email_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'price': 35.00,
    'currency': 'EUR',

}
