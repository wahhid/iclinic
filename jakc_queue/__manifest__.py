# -*- coding: utf-8 -*-
{
    'name': "Queue Management",
    'version': '10.0.0.1',
    'summary': """Queue Management System""",
    'description': """     
        Queue Management System
    """,
    'author': "Jakc Labs",
    'website': "http://www.jakc-labs.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Queue',
    # any module necessary for this one to work correctly
    'depends': ['base'],
    # always loaded
    'data': [
        'data/jakc_queue_data.xml',
        'security/jakc_queue_security.xml',
        'security/ir.model.access.csv',
        'views/jakc_queue_view.xml',
        'views/jakc_queue_menu.xml',
        'views/jakc_queue_pickup_dashboard.xml',
        'views/templates.xml',
        'views/routing_screen_templates.xml',
        'views/kiosk_screen_templates.xml',
        'views/pickup_screen_templates.xml',
        'views/report_queue_receipt_templates.xml',
        #'views/jakc_queue_report.xml',
        'report/report_queue_receipt_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}