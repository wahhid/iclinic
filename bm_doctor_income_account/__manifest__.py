# -*- coding: utf-8 -*-

{
    "name" : "OeHealth Doctor Income Account",
    "version" : "1.0",
    "author" :"Permata Technology, Ibrahim",
    "category": "HR",
    "description" :
    '''
    This module manage doctor income account to replace product income account.
    ''',
    "depends" : [
        "oehealth"
    ],
    "init_xml": [],
    "data": [
        "views/doctor_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}