import logging
from datetime import timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class medical_evaluation_patient(models.Model):
    _inherit = 'oeh.medical.evaluation'

    PENDIDIKAN = [
     ('SD', 'SD'),
     ('SMP', 'SMP'),
     ('SMA', 'SMA'),
     ('D3', 'D3'),
     ('S1', 'S1'),
     ('S2', 'S2'),
     ('S3', 'S3')]

    EMOSI = [
        ('emosi1', 'Tidak bisa menahan diri'),
        ('emosi2', 'Mudah Tersinggung'),
        ('emosi3', 'Gelisah'),
        ('emosi4', 'Tenang')]

    TEMPAT_TINGGAL = [
        ('tinggal1', 'Sendiri'),
        ('tinggal2', 'Sewa'),
        ('tinggal3', 'Bersama Keluarga Lain')]

    PENURUNAN_BB = [
        ('bb1', 'Tidak'),
        ('bb2', 'Tidak Yakin (ada tanda: baju menjadi lebih longgar)'),
        ('bb3', 'Penurunan BB sebanyak 1-5kg'),
        ('bb4', 'Penurunan BB sebanyak 6-10kg'),
        ('bb5', 'Penurunan BB sebanyak 11-15kg'),
        ('bb6', 'Penurunan BB sebanyak > 15kg'),
        ('bb7', 'Tidak tahu berapa kg penurunannya')]

    dm_stroke_p = fields.Boolean(string='DM Stroke')
    dm_stroke_k = fields.Boolean(string='DM Stroke')
    katarak = fields.Boolean(string='Katarak')
    hipertensi_p = fields.Boolean(string='Hipertensi')
    hipertensi_k = fields.Boolean(string='Hipertensi')
    jantung_p = fields.Boolean(string='Coronary heart disease')
    jantung_k = fields.Boolean(string='Coronary heart disease')
    kolesterol = fields.Boolean(string='Cholesterol, Kidney Disease ')
    liver = fields.Boolean(string='Liver ')
    asam_urat = fields.Boolean(string='Asam Urat ')
    pendarahan = fields.Boolean(string='Old Bleeding ')
    serangan_jantung = fields.Boolean(string='Heart attack')
    gangguan_ginjal = fields.Boolean(string='Kidney disease')
    kejiwaan = fields.Boolean(string='Psychiatric / Depression ')
    lain_rpp = fields.Text(string='Other ')
    lain_rpk = fields.Text(string='Other ')

    alergi_obat_makanan = fields.Boolean(string='Drug & Food Allergies ')
    lain_alergi_obat_makanan = fields.Text(string='Other ')
    alkohol = fields.Boolean(string='Roko / Alkohol ')
    lain_kebiasaan = fields.Text(string='Lain-Lain ')

    bb_pekerjaan = fields.Boolean(string='Is the patients job related to hazardous materials?')
    sebutkan_bb = fields.Text(string='Other ')
    imt = fields.Float(string='IMT (BB/TB2/M)')

    tingkat_pendidikan = fields.Selection(PENDIDIKAN, string='Pendidikan', index=True)
    disorientasi = fields.Boolean(string='Disorientasi ')
    sebutkan_disorientasi = fields.Text(string='Other ')
    emosi = fields.Selection(EMOSI, string='Emosi', index=True)
    tinggal = fields.Selection(TEMPAT_TINGGAL, string='Tempat Tinggal', index=True)

    bantuan_makan = fields.Boolean(string='Eat ')
    bantuan_mandi = fields.Boolean(string='Bathe ')
    bantuan_bak = fields.Boolean(string='BAK ')
    bantuan_bab = fields.Boolean(string='BAB ')
    bantuan_berjalan = fields.Boolean(string='Walk ')

    # Has the patient experienced any unplanned/unwanted weight loss in the last 6 months?
    penurunan_bb = fields.Selection(PENURUNAN_BB, string='Penurunan BB', index=True)

    #Is the patient's food intake reduced due to decreased appetite/difficulty accepting food?
    asupan_makan = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Asupan Makan Pasien', index=True)

    riwayat_jatuh = fields.Boolean(string='Riwayat Jatuh')
    diagnosa_sekunder = fields.Boolean(string='Diagnosa Sekunder')
    alat_bantu_jalan = fields.Selection([('abj1', 'Bed Resi/Dibantu Perawat'),('abj2', 'Kruk/Tongkat/Walker'),('abj3', 'Berpegangan pada kursi/lemari/meja')], string='Alat Bantu Jalan', index=True)
    cara_berjalan = fields.Selection([('cb1', 'Bed Resi/Dibantu Perawat'),('cb2', 'Kruk/Tongkat/Walker'),('cb3', 'Berpegangan pada kursi/lemari/meja')], string='Cara Berjalan', index=True)
    terapi_intravena = fields.Boolean(string='Terapi Intravena')
    status_mental = fields.Boolean(string='Status Mental')

    tujuan = fields.Text(string='Tujuan ')
    resiko = fields.Text(string='Resiko ')
    komplikasi = fields.Text(string='komplikasi ')
    alternatif = fields.Text(string='Alternatif ')

    tekanan_darah = fields.Float(string='Tekanan Darah (mmHg) ')
    nadi = fields.Float(string='Nadi (mmHg) ')
    total_gcs = fields.Float(string='Total GCS')
    gcs_e = fields.Float(string='GCS E')
    gcs_v = fields.Float(string='GCS V')
    gcs_m = fields.Float(string='GCS M')
    gds = fields.Float(string='GDS (mg/dl)')

    organ_atas = fields.Text(string='Kepala dan Leher')
    organ_jantung = fields.Text(string='Jantung')
    organ_perut = fields.Text(string='Perut')
    organ_anggota_gerak = fields.Text(string='Anggota Gerak')
    organ_genetalia = fields.Text(string='Genetalia')






