from odoo import api, fields, models, tools, _


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

    dm_p = fields.Boolean(string='Diabetes Meletus (DM)')
    dm_stroke_p = fields.Boolean(string='Stroke')
    dm_k = fields.Boolean(string='Diabetes Meletus (DM)')
    dm_stroke_k = fields.Boolean(string='Stroke')
    katarak = fields.Boolean(string='Katarak')
    hipertensi_p = fields.Boolean(string='Hipertensi')
    hipertensi_k = fields.Boolean(string='Hipertensi')
    jantung_p = fields.Boolean(string='Penyakit jantung koroner')
    jantung_k = fields.Boolean(string='Penyakit jantung koroner')
    kolesterol = fields.Boolean(string='Kolesterol')
    penyakit_ginjal = fields.Boolean(string='Penyakit Ginjal')
    liver = fields.Boolean(string='Liver ')
    asam_urat = fields.Boolean(string='Asam Urat')
    pendarahan = fields.Boolean(string='Pendarahan Lama')
    serangan_jantung = fields.Boolean(string='Serangan Jantung')
    gangguan_ginjal = fields.Boolean(string='Penyakit ginjal')
    kejiwaan = fields.Boolean(string='Psikiatri / Depresi ')
    lain_rpp = fields.Text(string='Sebutkan ')
    lain_rpk = fields.Text(string='Sebutkan ')

    alergi_obat_makanan = fields.Boolean(string='Alergi Makanan / Obat ')
    lain_alergi_obat_makanan = fields.Text(string='Sebutkan ')
    ketidaksukaan_makan = fields.Char(string="Ketidak Sukaan Makan")
    pantangan_makan = fields.Char(string="Pantangan Makan")
    pengalaman_diet = fields.Selection([('ada','Ada'), ('tidak','Tidak')], string="Pengalaman Diet")
    alkohol = fields.Boolean(string='Roko / Alkohol ')
    lain_kebiasaan = fields.Text(string='Lain-Lain ')

    bahan_berbahaya_pekerjaan = fields.Boolean(string='Pekerjaan Dengan Bahan Berbahaya? Misal,kimia,gas,dll')
    sebutkan_bahan_berbahaya = fields.Text(string='Sebutkan ')
    imt = fields.Float(string='IMT (BB/TB2/M)')

    tingkat_pendidikan = fields.Selection(PENDIDIKAN, string='Pendidikan', index=True)
    disorientasi = fields.Boolean(string='Disorientasi ')
    sebutkan_disorientasi = fields.Text(string='Sebutkan ')
    emosi = fields.Selection(EMOSI, string='Emosi', index=True)
    tinggal = fields.Selection(TEMPAT_TINGGAL, string='Tempat Tinggal', index=True)

    bantuan_makan = fields.Boolean(string='Bantuan Makan ')
    bantuan_mandi = fields.Boolean(string='Bantuan Mandi ')
    bantuan_bak = fields.Boolean(string='Bantuan BAK ')
    bantuan_bab = fields.Boolean(string='Bantuan BAB ')
    bantuan_berjalan = fields.Boolean(string='Bantuan Berjalan ')
    bantuan_berpakaian = fields.Boolean(string='Bantuan Berpakaian ')

    # Has the patient experienced any unplanned/unwanted weight loss in the last 6 months?
    penurunan_bb = fields.Selection(PENURUNAN_BB, string='Penurunan BB', index=True)

    #Is the patient's food intake reduced due to decreased appetite/difficulty accepting food?
    asupan_makan = fields.Selection([('yes', 'Yes'),('no', 'No')], string='Asupan Makan Pasien', index=True)

    riwayat_jatuh = fields.Boolean(string='Riwayat Jatuh')
    diagnosa_sekunder = fields.Boolean(string='Diagnosa Sekunder')
    kesadaran = fields.Char(string="Kesadaran")
    alat_bantu_jalan = fields.Selection([('abj1', 'Bed Resi/Dibantu Perawat'),('abj2', 'Kruk/Tongkat/Walker'),('abj3', 'Berpegangan pada kursi/lemari/meja')], string='Alat Bantu Jalan', index=True)
    cara_berjalan = fields.Selection([('cb1', 'Bed Resi/Dibantu Perawat'),('cb2', 'Kruk/Tongkat/Walker'),('cb3', 'Berpegangan pada kursi/lemari/meja')], string='Cara Berjalan', index=True)
    terapi_intravena = fields.Boolean(string='Terapi Intravena')
    status_mental = fields.Boolean(string='Status Mental')

    tujuan = fields.Text(string='Tujuan ')
    resiko = fields.Text(string='Resiko ')
    komplikasi = fields.Text(string='komplikasi ')
    alternatif = fields.Text(string='Alternatif ')

    nadi = fields.Float(string='Nadi (mmHg) ')
    total_gcs = fields.Float(string='Total GCS')
    gcs_e = fields.Float(string='GCS E')
    gcs_v = fields.Float(string='GCS V')
    gcs_m = fields.Float(string='GCS M')
    gds = fields.Float(string='GDS (mg/dl)')

    organ_atas = fields.Text(string='Kepala dan Leher')
    organ_paru = fields.Text(string='Paru')
    organ_jantung = fields.Text(string='Jantung / Paru')
    organ_perut = fields.Text(string='Perut')
    organ_anggota_gerak = fields.Text(string='Anggota Gerak')
    organ_genetalia = fields.Text(string='Genetalia')

    # KEBUTUHAN ELIMINASI
    frekuensi_bab = fields.Char(string='Frekuensi BAB')
    warna_bab = fields.Char(string='Warna BAB')
    konsistensi_bab = fields.Char(string='Konsistensi BAB')
    frekuensi_bak = fields.Char(string='Frekuensi BAK')
    jumlah_bak = fields.Char(string='Jumlah BAK')
    warna_bak = fields.Char(string='Warna BAK')

    # KEBUTUHAN AKTIVITAS DAN ISTIRAHAT
    olahraga = fields.Selection([('ya','Ya'),('tidak','Tidak')], string='Olahraga')
    obat_tidur = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Obat Tidur')
    kwalitas_tidur = fields.Selection([('nyenyak','Nyenyak'),('sering_terbangun','Sering Terbangun')], string='Kwalitas Tidur')
    keterbatasan_rom = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Keterbatasan ROM')

    # PENGKAJIAN NYERI
    pengkajian_nyeri_p = fields.Char(string='P')
    pengkajian_nyeri_q = fields.Char(string='Q')
    pengkajian_nyeri_r = fields.Char(string='R')
    pengkajian_nyeri_s = fields.Char(string='S')
    pengkajian_nyeri_t = fields.Char(string='T')
    
    # KEBUTUHAN EMOSIONAL
    kontak_mata = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Kontak Mata')
    bingung = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Bingung')
    perasaan_tidak_mampu = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Perasaan Tidak Mampu')
    perasaan_tidaK_berharga = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Perasaan Tidak Berharga')

    # CAIRAN DAN ELEKTROLIT
    minum = fields.Char(string='Minum')
    parenteral = fields.Char(string='Parenteral')
    mukosa_bibir = fields.Char(string='Mukosa Bibir')
    turgor_kulit = fields.Char(string='Turgor Kulit')
    edema = fields.Char(string='Edema')
    cairan_lain = fields.Char(string='Lain-lain')

    # KEBUTUHAN PERSEPSI SENSORI
    penglihatan = fields.Selection([('normal','Normal'),('tidak','Tidak Normal')], string='Penglihatan')
    pendengaran = fields.Selection([('normal','Normal'),('tidak','Tidak Normal')], string='Pendengaran')
    penciuman = fields.Selection([('normal','Normal'),('tidak','Tidak Normal')], string='Penciuman')
    pengecapan = fields.Selection([('normal','Normal'),('tidak','Tidak Normal')], string='Pengecapan')
    perabaan = fields.Selection([('normal','Normal'),('tidak','Tidak Normal')], string='Perabaan')

    # KEBUTUHAN KOMUNIKASI
    pembicaraan = fields.Selection([('koheren','Koheren'),('tidak','Tidak Normal')], string='Penglihatan')
    apatis = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Apatis')
    afasia = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Afasia')

    kegiatan_ibadah = fields.Text(string='Kegiatan Ibada Sehari hari')

    # Anthropometry
    status_gizi = fields.Char(string='Status Gizi')
    berat_badan_biasanya = fields.Float(string='BB Biasanya (kg)')
    penurunan_berat_badan = fields.Float(string='Penurunan BB (%)')
    penurunan_berat_badan_dalam = fields.Char(string='Penurunan Dalam (mgg bln)')
    pengukuran_lain = fields.Text(string='Pengukuran lain')

    # BIOKIMIA TERKAIT GIZI
    prosedur_terkait_gizi = fields.Text(string='Prosedur')

    # Fisik Klinis Gizi
    atropi = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Atropi Otot Lengan')
    udem = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Udem')
    nafsu_makan = fields.Selection([('baik','Baik'),('tidak','Tidak')], string='Nafsu Makan')
    mual = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Mual')
    muntah = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Muntah')
    kembung = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Kembung')
    konstipasi = fields.Selection([('ada','Ada'),('tidak','Tidak')], string='Konstipasi')
    diare = fields.Selection([('baik','Baik'),('tidak','Tidak')], string='Diare')
    kepaladanmata = fields.Char(string="Kepala Dan Mata")
    fisik_gizi_kulit = fields.Char(string="Kulit")
    gigi_geligi = fields.Char(string="Gigi Geligi")
    ganguan_menelan = fields.Char(string="Gangguan Menelan")
    ganguan_mengunyah = fields.Char(string="Gangguan Mengunyah")
    ganguan_menghisap = fields.Char(string="Gangguan Menghisap")

    peran_dlm_keluarga = fields.Char(string="Peran Dalam Keluarga")
    mobilitas = fields.Char(string="Mobilitas")
    keterbatasan_fisik = fields.Char(string="Keterbatasan Fisik")
    






