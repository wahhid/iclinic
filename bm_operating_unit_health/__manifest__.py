# -*- coding: utf-8 -*-

{
    "name" : "Operating Unit Health",
    "version" : "1.0",
    "author" :"Permata Technology, Ibrahim",
    "category": "Extra Tools",
    "description" :
    '''
    This module manage operating unit in health module.
    ''',
    "depends" : [
        "operating_unit",
        "stock"
    ],
    "init_xml": [],
    "data": [
        "security/ir.model.access.csv",

        "views/unit_view.xml",
        "views/stock_view.xml",
        "views/menu_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}