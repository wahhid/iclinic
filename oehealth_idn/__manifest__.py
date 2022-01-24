# -*- coding: utf-8 -*-
{
    "name" : "Hospital Management System",
    "version" : "10.0.2.0",
    "author" :"WEHA Consultant",
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
        "stock",
        "jakc_queue",
        "operating_unit"
    ],
    "init_xml": [],
    "data": [
        "data/sequence.xml",
        "security/res.groups.xml",
        "security/ir.rule.xml",
        "security/ir.model.access.csv",
        "wizard/ms_report_stock_wizard.xml",
        "wizard/wizard_reference_hospital.xml",
        "wizard/wizard_report_physician_income.xml",
        "wizard/wizard_next_step.xml",
        "views/medical_physician_view.xml",
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
        "views/jakc_queue_view.xml",
        "views/res_users_view.xml",
        "views/unit_view.xml",
        "views/menu_view.xml",
        "config/sale_config_settings.xml",
        "wizard/ms_report_stock_wizard.xml",
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
        "report/konsultasi_report.xml",
        "report/rujukan_radiologi_report.xml",
        "report/rujukan_pasien_report.xml",
        "report/persetujuan_tindakan_report.xml",
        "report/registration_reciept.xml",
        "report/catatan_asuhan_gizi_report.xml",
        "report/catatan_registrasi_pasien_report.xml",
        "report/surat_keterangan_report.xml",
        "report/observasi_terapi_pasien_report.xml",
        "report/rujukan_poli_gigi_report.xml",
        "report/pemeriksaan_poli_gigi_report.xml",
        "report/pengkajian_rawat_inap_report.xml",
        # "report/rekam_medis_rawat_jalan_report.xml",
        "report/cppt_report.xml",
        "report/implementasi_keperawatan_report.xml",
        "report/rujukan_internal_report.xml",
        "report/persetujuan_tindakan_report.xml",
        "report/registration_reciept.xml",
        "report/report_physician_income_template.xml",
        "report/report_physician_income.xml",
        "report/pengkajian_rawat_jalan_report.xml",
        "report/perintah_rawat_inap_report.xml",
        "report/report_rekam_medis_rawat_jalan_template.xml",
        "report/report_rekam_medis_rawat_jalan.xml",
        "report/report_patient_labtest.xml",
        "report/resep_report.xml",
        "report/report_menu.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}