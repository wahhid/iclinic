{
	"name": "Stock Card", 
	"version": "1.0", 
	"depends": [
		"stock"
	], 
	"author": "Akhmad D. Sembiring [vitraining.com]",
	"website": "www.vitraining.com",
    'category': 'Accounting',
	'images': ['static/description/images/main_screenshot.jpg'],
	'price':'30',
    'currency': 'USD',
	"category": "Warehouse",
	"summary" : "This modul to display stock card per product per Warehouse and product summary per Warehouse",
	"description": """\

Manage
======================================================================

* this modul to display stock card per item per Warehouse
* this modul to display stock card summary per Warehouse


""",
	"data": [
		"menu.xml", 
		"view/stock_card.xml", 
		"view/stock_summary.xml",
		"report/stock_card.xml",
		"data/ir_sequence.xml",
		"security/ir.model.access.csv",
	],
	"application": True,
	"installable": True,
	"auto_install": False,
}