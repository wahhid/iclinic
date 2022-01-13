# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.9 (default, Jan 26 2021, 15:33:00) 
# [GCC 8.4.0]
# Embedded file name: D:\Workspaces\Odoo10\mod\Health\addons-custom\oehealth_idn\models\prescription.py
# Compiled at: 2018-11-22 17:20:13
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
import datetime
import logging

_logger = logging.getLogger(__name__)

#Prescription
class oeh_medical_prescription(models.Model):
    _inherit = 'oeh.medical.prescription'

    PAYMENT_TYPE = [
        ('Personal', 'Personal'),
        ('Corporate', 'Corporate'),
        ('Insurance', 'Insurance'),
        ('Employee', 'Employee')
    ]

    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    insurance = fields.Many2one(comodel_name='medical.insurance', string='Insurance', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    employee_id = fields.Many2one('oeh.medical.patient', 'Employee', readonly=True)
    payment_guarantor_discount_id = fields.Many2one('payment.guarantor.discount', 'Payment Guarantor Discount')
    concoction_ids = fields.One2many('medical.concoction', 'prescription_id', copy=True, string='Concoction')

    @api.model
    def create(self, vals):
        res = super(oeh_medical_prescription, self).create(vals)
        if res.payment == 'Personal':
            #Personal
            domain = [
                ('payment','=', 'Personal')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id
        elif res.payment == 'Corporate':
            #Corporate
            _logger.info('Corporate')
            domain = [
                ('payment','=', 'Corporate'),
                ('company','=', res.company.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        elif res.payment == 'Insurance':
            #Insurance
            _logger.info('Insurance')
            domain = [
                ('payment','=', 'Insurance'),
                ('insurance_type_id','=', res.insurance.ins_type.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        else:
            #Employee
            domain = [
                ('payment','=', 'Employee')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id.id
        
        return res

    def action_prescription_send_to_pharmacy(self):
        pharmacy_obj = self.env['oeh.medical.health.center.pharmacy.line']
        pharmacy_line_obj = self.env['oeh.medical.health.center.pharmacy.prescription.line']
        medical_concoction_obj = self.env['medical.concoction']
        medical_concoction_detail_obj = self.env['medical.concoction.detail']

        res = {}
        for pres in self:
            if not pres.pharmacy:
                raise UserError(_('No pharmacy selected !!'))
            else:
                curr_pres = {
                    'name': pres.id, 
                    'reg_ids': pres.reg_id.id,
                    'patient': pres.patient.id, 
                    'doctor': pres.doctor.id, 
                    'pharmacy_id': pres.pharmacy.id, 
                    'state': 'Draft', 
                    'arrival_id': pres.walkin.id, 
                    'reg_id': pres.reg_id.id,
                    'payment': pres.payment,
                    'company': pres.company.id,
                    'insurance': pres.insurance.id,
                    'employee_id': pres.employee_id.id,
                    'queue_trans_id': pres.reg_id.queue_trans_id.id,
                    'pharmacist': pres.pharmacy.pharmacist_name.id,
                }
                phy_id = pharmacy_obj.create(curr_pres)
                
                if phy_id:
                    #Prescription Line
                    if pres.prescription_line:
                        for ps in pres.prescription_line:
                            curr_pres_line = {
                                'name': ps.name.id, 
                                'indication': ps.indication.id, 
                                'price_unit': ps.name.list_price, 
                                'qty': ps.qty, 
                                'actual_qty': ps.qty, 
                                'prescription_id': phy_id.id,
                                'state': 'draft'
                            }
                            pharmacy_line_obj.create(curr_pres_line)
                            
                    #Concoction Line
                    if pres.concoction_ids:
                        for cn in pres.concoction_ids:
                            #cn.prescription_line_id = phy_ids.id
                            cur_cn_lines = []
                            for detail_id in cn.concoction_detail_ids:
                                vals = (0,0,{
                                    'product_id': detail_id.product_id.id,
                                    #'big_qty': detail_id.big_qty, 
                                    'is_alt_uom': detail_id.is_alt_uom,
                                    'qty': detail_id.qty,
                                    'zat_qty': detail_id.zat_qty,
                                    'total': detail_id.total
                                })
                                cur_cn_lines.append(vals)

                            cur_cn = {
                                'prescription_line_id': phy_id.id, 
                                'product_id': cn.product_id.id, 
                                'item_type': cn.item_type,
                                'doctor_id': cn.doctor_id.id, 
                                'qty': cn.qty,
                                'qty_unit': cn.qty_unit,
                                'product_uom': cn.product_uom.id, 
                                'price': cn.price,
                                'remark': cn.remark,
                                'concoction_detail_ids': cur_cn_lines
                            }
                            medical_concoction_id = medical_concoction_obj.create(cur_cn)

                res = pres.write({'state': 'Sent to Pharmacy'})

        return True

class oeh_medical_prescription_line(models.Model):
    _inherit = 'oeh.medical.prescription.line'

    @api.onchange('name')
    def onchange_product(self):
        domain = [('unit_ids','in',(self.env.user.default_unit_administration_id.id))]
        stock_location_id = self.env['stock.location'].search(domain, limit=1)
        if stock_location_id:
            domain = [
                ('product_id','=',self.name.id),
                ('location_id','=', stock_location_id.id)
            ]
            _logger.info(domain)
            fields = ['product_id','qty']
            groupby = ['product_id']
            result = self.env['stock.quant'].read_group(domain, fields=fields, groupby=groupby)
            _logger.info(result)
            if len(result) > 0:
                self.qty_available = result[0]['qty']
            else:
                self.qty_available = 0.0

    name = fields.Many2one('product.product', string='Medicines', help='Prescribed Medicines', domain=[('item_type', '=', 'Medicine')], required=True)
    product_template_categ_id = fields.Many2one('product.template.category', related='name.product_template_categ_id')
    qty_available = fields.Float("Qty On Hand")

#Pharmacy Order

class oeh_medical_health_center_pharmacy(models.Model):
    _inherit = 'oeh.medical.health.center.pharmacy'
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True)

class oeh_medical_health_center_pharmacy_line(models.Model):
    _inherit = 'oeh.medical.health.center.pharmacy.line'
    
    PAYMENT_TYPE = [
        ('Personal', 'Personal'),
        ('Corporate', 'Corporate'),
        ('Insurance', 'Insurance'),
        ('Employee', 'Employee')
    ]

    @api.multi
    def view_picking(self, context):
        '''
        This function returns an action that display existing delivery orders
        of given sales order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.sale_order_id.mapped('picking_ids')
        _logger.info(pickings)
        if not pickings:
            _logger.info("No Picking")
            return False
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action
    
    @api.depends('prescription_lines.price_subtotal', 'concoction_ids.price')
    def amount_all(self):
        """
        Compute the total amounts of the Prescription lines.
        """
        for order in self:
            val = 0.0
            for line in order.prescription_lines:
                _logger.info(line.price_subtotal)
                val += line.price_subtotal

            for line in order.concoction_ids:
                _logger.info(line.price)
                val += line.price
            
            order.amount_total = val
            #order.update({'amount_total': val})

    def action_next(self):
        if not self.queue_trans_id:
            raise Warning('No Queue number defined!')

        if self.state == 'Draft':
            if len(self.clinic_ids) > 0  or len(self.unit_ids) > 0 or len(self.emergency_ids) > 0 or len(self.support_ids) > 0 or len(self.lab_test_ids) > 0:
                next_type_id = self.queue_trans_id.type_id.next_type_id
                self.queue_trans_id.write({'type_id' : next_type_id.id, 'state': 'draft'}) 
                self.state = 'Scheduled'
            else:
                raise Warning('Need min 1 unit registration!')
        else:
            next_type_id = self.queue_trans_id.type_id.next_type_id
            self.queue_trans_id.write({'type_id' : next_type_id.id, 'state': 'draft'})


    def get_user_unit_administration(self):
        for row in self:
            _logger.info(self.env.user.default_unit_administration_id.id)
            row.user_unit_administration_id = self.env.user.default_unit_administration_id.id

    name = fields.Many2one('oeh.medical.prescription', string='Prescription #', required=False, ondelete='cascade', readonly=True, states={'Draft': [('readonly', False)]})
    arrival_id = fields.Many2one(comodel_name='oeh.medical.appointment.register.walkin', string='Queue #')
    reg_id = fields.Many2one(comodel_name='unit.registration', string='Reference Reg ID')
    unit_id = fields.Many2one(comodel_name='unit.administration', related='reg_id.unit', string='Reference Unit')
    reg_ids = fields.Many2one(comodel_name='unit.registration', string='Registration')
    sale_order_id = fields.Many2one('sale.order', string='Order#', readonly=True)

    is_public = fields.Boolean('Is Public', default=False)
    remark = fields.Text('Remark')
    pharmacist = fields.Many2one('oeh.medical.physician', string='Pharmacist', help='Current primary care / family doctor', domain=[('is_pharmacist', '=', True)], required=True, readonly=True, states={'Draft': [('readonly', False)]})
    payment = fields.Selection(PAYMENT_TYPE, string='Payment Guarantor', default='Personal', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    company = fields.Many2one(comodel_name='res.partner', string='Company', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    insurance = fields.Many2one(comodel_name='medical.insurance', string='Insurance', readonly=True, states={'Draft': [('readonly', False)]}, track_visibility='onchange')
    employee_id = fields.Many2one('oeh.medical.patient', 'Employee', readonly=True)
    payment_guarantor_discount_id = fields.Many2one('payment.guarantor.discount', 'Payment Guarantor Discount')
    concoction_ids = fields.One2many('medical.concoction', 'prescription_line_id', copy=True, string='Concoction')

    queue_trans_id = fields.Many2one('queue.trans','Queue', domain=[('unit','','')])
    type_id = fields.Many2one('queue.type', related="queue_trans_id.type_id", readonly=True)
    user_unit_administration_id = fields.Many2one('unit.administration', compute="get_user_unit_administration")
    is_on_unit_administration = fields.Boolean('', compute="get_user_unit_administration")

    amount_total = fields.Monetary(compute=amount_all, string='Total', store=True, multi='sums', help='The total amount.')


    @api.model
    def create(self, vals):
        res = super(oeh_medical_health_center_pharmacy_line, self).create(vals)
        if res.payment == 'Personal':
            #Personal
            domain = [
                ('payment','=', 'Personal')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id
        elif res.payment == 'Corporate':
            #Corporate
            _logger.info('Corporate')
            domain = [
                ('payment','=', 'Corporate'),
                ('company','=', res.company.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        elif res.payment == 'Insurance':
            #Insurance
            _logger.info('Insurance')
            domain = [
                ('payment','=', 'Insurance'),
                ('insurance_type_id','=', res.insurance.ins_type.id)
            ]
            _logger.info(domain)
            payment_guarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_guarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            _logger.info(payment_guarantor_discount_id.description)
            res.payment_guarantor_discount_id = payment_guarantor_discount_id.id
        else:
            #Employee
            domain = [
                ('payment','=', 'Employee')
            ]
            payment_quarantor_discount_id = self.env['payment.guarantor.discount'].search(domain, limit=1)
            if not payment_quarantor_discount_id:
                raise Warning(_('Payment Guarantor Discount not found'))
            res.payment_quarantor_discount_id = payment_quarantor_discount_id.id
        
        return res

    @api.multi
    def create_sale(self):
        _logger.info('Create Sale')
        obj = self.env['sale.order']
        #obj2 = self.env['unit.registration']
        line_obj = self.env['sale.order.line']
        inv_ids = []
        guarantor = 0
        arrival = 0
        for acc in self:

            user_unit = self.env['unit.administration'].search([('operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id
            if not user_unit:
                raise UserError(_('Configuration Error! \n Could not Find default Operating Unit in User : ' + self.env.user.name))

            if not acc.is_public:
                if acc.reg_ids:
                    if acc.payment == 'Insurance':
                        guarantor = acc.insurance.ins_type.partner_id.id
                    elif acc.payment == 'Corporate':
                        guarantor = acc.company.id
                    elif acc.payment == 'Employee':
                        guarantor = acc.employee_id.current_insurance.ins_type.partner_id.id
                    else:
                        guarantor = acc.patient.partner_id.id
                    
                    _logger.info(self.env.user.default_operating_unit_id)
                    
                #  val_obj = {
                #     'reg_id': acc.id, 
                #     'arrival_id': acc.clinic_walkin_id.id or acc.unit_walkin_id.id or acc.emergency_walkin_id.id or acc.support_walkin_id.id, 
                #     'patient_id': acc.patient.id, 
                #     'doctor_id': acc.doctor.id, 
                #     'partner_id': acc.patient.partner_id.id, 
                #     'partner_invoice_id': guarantor, 
                #     'payment_guarantor_discount_id': acc.payment_guarantor_discount_id.id, 
                #     'partner_shipping_id': acc.patient.partner_id.id, 
                #     'pricelist_id': acc.charge_id.pricelist.id or acc.patient.partner_id.property_product_pricelist.id, 
                #     'location_id':  self.env['stock.location'].search([('unit_ids', 'in', (self.unit.id))], limit=1).id
                # }

                    val_obj = {
                        'reg_id': acc.reg_ids.id, 
                        'arrival_id': acc.arrival_id.id, 
                        'patient_id': acc.patient.id, 
                        'doctor_id': acc.doctor.id, 
                        'partner_id': guarantor, 
                        'partner_invoice_id': guarantor, 
                        'partner_shipping_id': acc.patient.partner_id.id, 
                        'payment_guarantor_discount_id': acc.payment_guarantor_discount_id.id, 
                        'operating_unit_id': self.env.user.default_operating_unit_id.id,
                        #'user_id': self.env.user.id,
                        'location_id':  self.env['stock.location'].search([('unit_ids', 'in', (self.env.user.default_operating_unit_id.id))], limit=1).id
                        #'location_id': self.env['stock.location'].search([('unit_ids.operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id,
                    }
                    _logger.info(val_obj)
                    inv_ids = obj.sudo().create(val_obj)
                    
                    if inv_ids:
                        inv_id = inv_ids.id
                        # No Need Auto Billing
                        # if self.arrival_id and not self.arrival_id.have_register:
                        #     product = self.env['product.product'].search([('auto_billing', '!=', False)])
                        #     for p in product:
                        #         vals = {'order_id': inv_id, 'product_id': p.id, 
                        #         'name': p.name, 
                        #         'product_uom_qty': 1, 
                        #         'product_uom': p.uom_id.id, 
                        #         'price_unit': p.lst_price}
                        #         line_obj.create(vals)

                        arrival = self.env['oeh.medical.appointment.register.walkin'].browse(self.arrival_id.id)
                        arrival.write({'have_register': True})
                        
                        if acc.prescription_lines:
                            for ps in acc.prescription_lines:
                                discount = 0.0
                                product_id = ps.name
                                if acc.payment_guarantor_discount_id:
                                    if product_id.item_type == 'General Item':
                                        discount = acc.payment_guarantor_discount_id.general_item
                                    elif product_id.item_type == 'Medical Item':        
                                        discount = acc.payment_guarantor_discount_id.medical_item
                                    elif product_id.item_type == 'Food Item':        
                                        discount = acc.payment_guarantor_discount_id.food_item
                                    elif product_id.item_type == 'Medicine':        
                                        discount = acc.payment_guarantor_discount_id.medicine
                                    elif product_id.item_type == 'Doctor':        
                                        discount = acc.payment_guarantor_discount_id.doctor
                                    elif product_id.item_type == 'Nurse':        
                                        discount = acc.payment_guarantor_discount_id.nurse
                                vals = {
                                    'order_id': inv_id, 
                                    'product_id': ps.name.id, 
                                    'name': ps.name.name, 
                                    'prescribe_qty': ps.qty, 
                                    'product_uom_qty': ps.actual_qty, 
                                    'product_uom': ps.name.uom_id.id, 
                                    'discount_type': 'percent',
                                    'discount': discount,
                                    #product_uom': ps.name.uom_id.id, 
                                    'price_unit': ps.price_unit
                                }
                                _logger.info(vals)
                                line_obj.sudo().create(vals)

                        if acc.concoction_ids:
                            for cn in acc.concoction_ids:
                                for cnd in cn.concoction_detail_ids:
                                    discount = 0.0
                                    product_id = ps.name
                                    if acc.payment_guarantor_discount_id:
                                        if product_id.item_type == 'General Item':
                                            discount = acc.payment_guarantor_discount_id.general_item
                                        elif product_id.item_type == 'Medical Item':        
                                            discount = acc.payment_guarantor_discount_id.medical_item
                                        elif product_id.item_type == 'Food Item':        
                                            discount = acc.payment_guarantor_discount_id.food_item
                                        elif product_id.item_type == 'Medicine':        
                                            discount = acc.payment_guarantor_discount_id.medicine
                                        elif product_id.item_type == 'Doctor':        
                                            discount = acc.payment_guarantor_discount_id.doctor
                                        elif product_id.item_type == 'Nurse':        
                                            discount = acc.payment_guarantor_discount_id.nurse
                                    vals = {
                                        'order_id': inv_id, 
                                        'product_id': cnd.product_id.id, 
                                        'name': cnd.product_id.name, 
                                        'is_concoction': True,
                                        'medical_concoction_id': cn.id,
                                        'prescribe_qty': cnd.qty, 
                                        'product_uom_qty': cnd.total, 
                                        'product_uom': cnd.uom_id.id, 
                                        #'price_unit': cnd.price_unit
                                    }
                                    line_obj.sudo().create(vals)

                    self.write(
                        {
                            'state': 'Invoiced',
                            'sale_order_id': inv_id
                        }
                    )
                    inv_ids.action_confirm()
                else:
                    raise UserError(_('Configuration Error! \n Could not Find Registration to Create the Transactions !'))
            else:
                val_obj = {
                    'reg_id': False, 
                    'arrival_id': False, 
                    'patient_id': acc.patient.id, 
                    'doctor_id': acc.doctor.id, 
                    'partner_id': guarantor, 
                    'partner_invoice_id': guarantor, 
                    'partner_shipping_id': guarantor, 
                    'payment_guarantor_discount_id': acc.payment_guarantor_discount_id.id,
                    'operating_unit_id': self.env.user.default_operating_unit_id.id,
                    'location_id': self.env['stock.location'].search([('unit_ids.operating_id', '=', self.env.user.default_operating_unit_id.id)], limit=1).id}
                inv_ids = obj.create(val_obj)
                
                if inv_ids:
                    inv_id = inv_ids.id
                    if acc.prescription_lines:
                        for ps in acc.prescription_lines:
                            vals = {
                                'order_id': inv_id, 
                                'product_id': ps.name.id, 
                                'name': ps.name.name, 
                                'prescribe_qty': ps.qty, 
                                'product_uom_qty': ps.actual_qty, 
                                'product_uom': ps.name.uom_id.id, 
                                'price_unit': ps.price_unit
                            }
                            line_obj.create(vals)

                        if acc.concoction_ids:
                            for cn in acc.concoction_ids:
                                for cnd in cn.concoction_detail_ids:
                                    discount = 0.0
                                    product_id = ps.name
                                    if acc.payment_guarantor_discount_id:
                                        if product_id.item_type == 'General Item':
                                            discount = acc.payment_guarantor_discount_id.general_item
                                        elif product_id.item_type == 'Medical Item':        
                                            discount = acc.payment_guarantor_discount_id.medical_item
                                        elif product_id.item_type == 'Food Item':        
                                            discount = acc.payment_guarantor_discount_id.food_item
                                        elif product_id.item_type == 'Medicine':        
                                            discount = acc.payment_guarantor_discount_id.medicine
                                        elif product_id.item_type == 'Doctor':        
                                            discount = acc.payment_guarantor_discount_id.doctor
                                        elif product_id.item_type == 'Nurse':        
                                            discount = acc.payment_guarantor_discount_id.nurse
                                    vals = {
                                        'order_id': inv_id, 
                                        'product_id': cnd.product_id.id, 
                                        'name': cnd.product_id.name, 
                                        'is_concoction': True,
                                        'medical_concoction_id': cn.id,
                                        'prescribe_qty': cnd.qty, 
                                        'product_uom_qty': cnd.total, 
                                        'product_uom': cnd.uom_id.id, 
                                        'discount_type': 'percent',
                                        'discount': discount,
                                        'price_unit': cnd.product_id.lst_price
                                    }
                                    line_obj.create(vals)

                self.write(
                    {
                        'state': 'Invoiced',
                        'sale_order_id': inv_id
                    }
                )
                inv_ids.action_confirm()

class oeh_medical_health_center_pharmacy_prescription_line(models.Model):
    _inherit = 'oeh.medical.health.center.pharmacy.prescription.line'
    
    @api.multi
    @api.onchange('name')
    def onchange_name(self, name=False):
        _logger.info('On Change Name')
        result = {}
        if name:
            product_ids = self.env['product.product'].search([('id','=',name)])
            if product_ids:
                result['price_unit'] = product_ids.lst_price
        return {'value': result}
    

    name = fields.Many2one('product.product', string='Medicines', help='Prescribed Medicines', domain=[('item_type', '=', 'Medicine')], required=True)
    qty_available = fields.Float(related='name.qty_available')
    actual_qty = fields.Integer(string='Actual Qty Given', help='Actual quantity given to the patient', default=1)
