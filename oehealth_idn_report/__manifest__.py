{
    'name': 'WEHA - oehealth_idn report',
    'version': '10.0.0.1',
    'category': 'purchase',
    'summary': 'This apps help to define a discount per line in the purchase orders.',
    'description': """
        In this module you can add discounts in purchase lines.
        You will get discount on purhcase reports.
        Discounts in Purchase order lines
""",
    'license':'OPL-1',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'images': [],
    'depends': ['base','purchase'],
    'data': [
            'views/purchase.xml',
            'report/inherit_purchase_report.xml'
    ],
    'installable': True,
    'auto_install': False,
}

