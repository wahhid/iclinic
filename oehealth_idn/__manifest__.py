# -*- coding: utf-8 -*-

{
    "name" : "Indonesia Hospital Management System",
    "version" : "2.0",
    "author" :"Permata Technology, Ibrahim",
    "category": "Medical",
    "description" :
    '''
    This module manage hospital.
    Please install addons "vit_kelurahan" before install this.
    ''',
    "depends" : [
        "oehealth",
        "oehealth_extra_addons",
        "bm_operating_unit_health",
        "sale_stock_location",
        "vit_kelurahan",
        "sale_margin",
        "stock"
    ],
    "init_xml": [],
    "data": [
        "data/sequence.xml",
        "security/res.groups.xml",
        "security/ir.rule.xml",
        "security/ir.model.access.csv",

        "views/medical_evaluation_view.xml",
        "views/class_view.xml",
        "views/room_view.xml",
        "views/insurance_view.xml",
        "views/unit_registration_view.xml",
        "views/unit_registration_action_view.xml",
        "views/appointment_view.xml",
        "views/patient_view.xml",
        "views/res_partner_view.xml",
        "views/doctor_view.xml",
        "views/product_view.xml",
        "views/registration_view.xml",
        "views/sale_order_view.xml",
        "views/concoction_view.xml",
        "views/labtest_view.xml",
        "views/prescription_view.xml",
        "views/opthalmology_view.xml",
        "views/account_invoice_view.xml",
        "views/stock_pack_operation_views.xml",
        "views/menu_view.xml",

        "config/sale_config_settings.xml",
        "wizard/sale_order_line_make_account_invoice_view.xml",

        "report/patient_card_report.xml",
        "report/stiker_pasien_report.xml",
        "report/master_filepatient_report.xml",
        "report/daftar_transaksi_detail_report.xml",
        "report/daftar_transaksi_report.xml",
        "report/nota_resep_report.xml",
        "report/salinan_resep_report.xml",
        "report/detail_transaksi_invoice_report.xml",
        "report/kwitansi_report.xml",
        "report/slip_registrasi_rajal_report.xml",
        "report/slip_registrasi_penunjang_report.xml",
        "report/slip_registrasi_igd_report.xml",
        "report/prescription_etiket_report.xml",
        "report/report_menu.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}