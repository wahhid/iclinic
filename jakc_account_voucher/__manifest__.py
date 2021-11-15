# -*- coding: utf-8 -*-

{
    'name': 'WEHA - Account Voucher Enhancement',
    'version': '10.0.0.1.0',
    'category': 'General',
    'license': 'AGPL-3',
    'summary': 'Account Voucher Enchancement',
    'author': "WEHA Consultant",
    'website': 'http://www.weha-id.com/',
    'depends': [
        'account_voucher'
    ],
    'data': [
        'views/jakc_account_voucher_view.xml',
        'views/jakc_res_users_view.xml',
        'report/account_voucher_report.xml',
        'report/account_voucher_templates.xml',
    ],
    'installable': True,
    'application': True,
}
