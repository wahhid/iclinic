# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

from datetime import datetime
import json
import werkzeug
import logging

_logger = logging.getLogger(__name__)


class QueuePickup(http.Controller):

    @http.route('/queue/pickup/listall', auth='public')
    def category_list(self, **kw):
        env_type = http.request.env['queue.pickup']
        args = [('state', '=', 'open')]
        type_ids = env_type.sudo().search_read(args)
        return json.dumps(type_ids)

    @http.route('/queue/pickupui/', auth='public')
    def pickupui(self, **kw):    
        env_pickup = http.request.env['queue.pickup']
        pickups = env_pickup.sudo().search([])
        return request.render('jakc_queue.pickupui', {'pickups': pickups})

    @http.route('/queue/pickup/screen/<pickup_code>', type='http', auth='public')
    def queue_pickup_screen(self, pickup_code):
        # if user not logged in, log him in
        queue_trans_obj = http.request.env['queue.trans']
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_pickup_id = queue_pickup_obj.sudo().search([('name','=',pickup_code)],limit=1)
        # pickup_log = http.request.env['queue.pickup.log'].sudo().search([
        #     ('state', '=', 'opened'),
        #     ('pickup_id', '=', queue_pickup_id.id) ], limit=1)
        # if pickup_log:
        #     _logger.info(pickup_log)
        pickup_data = {}
        pickup_data.update({'pickup_id': queue_pickup_id.id})
        return request.render('jakc_queue.pickupscreen', {'pickup': pickup_data})


    @http.route('/queue/pickup/current/<int:pickup_id>/', type='http', auth='public')
    def queue_pickup_current(self, pickup_id, **kwargs):
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_pickup_log_obj = http.request.env['queue.pickup.log']
        queue_trans_obj = http.request.env['queue.trans']
        pickup = queue_pickup_obj.sudo().browse(pickup_id)
        if pickup:
            #trans_args = [('state', '=', 'open'), ('type_id', '=', pickup.type_id.id)]
            trans_args = [
                ('trans_date','=', datetime.now().strftime('%Y-%m-%d')),
                ('state', '=', 'open'), 
                ('pickup_id','=', pickup.id),
                ('type_id', '=', pickup.type_id.id)
            ]
            trans_id = queue_trans_obj.sudo().search(trans_args, limit=1, order="write_date")
            if trans_id:
                trans_data = {}
                trans_data.update({'id': trans_id.id})
                trans_data.update({'counter_trans': trans_id.trans_id})
                trans_data.update({'counter_name': trans_id.type_id.name})
                trans_data.update({'counter_bg': trans_id.type_id.bg_color})
                return json.dumps(trans_data)
            else:
                return '{"success":false,"message":"No Queue"}'
        else:
            return '{"success":false,"message":"No Queue"}'

    @http.route('/queue/pickup/<int:id>/', auth='public')
    def pickup(self, id):
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_pickup_log_obj = http.request.env['queue.pickup.log']
        queue_trans_obj = http.request.env['queue.trans']
        pickup = queue_pickup_obj.browse(id)
        if pickup:
            trans_args = [
                ('trans_date','=', datetime.now().strftime('%Y-%m-%d')),
                ('state', '=', 'draft'), 
                ('type_id', '=', pickup.type_id.id)
            ]
            trans_id = queue_trans_obj.sudo().search(trans_args, order='write_date', limit=1)
            if trans_id:
                trans_id.write({'pickup_date_time': datetime.now(),
                                'state': 'open',
                                'type_id': pickup.type_id.id,
                                'iface_recall': True,
                                'recall_date_time': datetime.now(),
                                'pickup_id': pickup.id})
                trans_data = {}
                trans_data.update({'id': trans_id.id})
                trans_data.update({'counter_trans': trans_id.trans_id})
                trans_data.update({'counter_name': trans_id.type_id.name})
                trans_data.update({'counter_bg': trans_id.type_id.bg_color})
                return json.dumps(trans_data)
            else:
                return '{"success":false,"message":"No Queue"}'
        else:
            return '{"success":false,"message":"No Queue"}'

    @http.route('/queue/recall/<int:id>/', auth='public')
    def recall(self, id, **kwargs):
        queue_trans_obj = http.request.env['queue.trans']
        trans = queue_trans_obj.sudo().browse(id)
        trans.write({'recall_date_time': datetime.now(), 'iface_recall': True})
        return json.dumps({'status': True})

    @http.route('/queue/finish/<int:id>/', auth='public')
    def finish(self, id):
        queue_trans_obj = http.request.env['queue.trans']
        queue_trans_id = queue_trans_obj.browse(id)
        if not queue_trans_id:
            return json.dumps({'status': False})
        
        if queue_trans_id.state == 'open':
            queue_trans_id.write({'end_date_time': datetime.now(), 'state': 'done'})
            return json.dumps({'status': True})
    
        # if trans.state != 'done':
        #     trans.write({'pickup_id': False})   
        # else:
        #     trans.write({'end_date_time': datetime.now(), 'state': 'done'})
        return json.dumps({'status': False})

    @http.route('/queue/skip/<int:id>/', auth='public')
    def skip(self, id):
        queue_trans_obj = http.request.env['queue.trans']
        trans = queue_trans_obj.sudo().browse(id)
        trans.write({'end_date_time': datetime.now(), 'state': 'done'})
        return json.dumps({'status': True})

class Queue_display(http.Controller):
    
    @http.route('/queue/displayui/<display_code>/', auth='public')
    def displayui(self, display_code, **kw):
        return request.render('jakc_queue.index', {'displaycode': display_code})

    @http.route('/queue/routeui/', auth='public')
    def routeui(self, **kw):
        return request.render('jakc_queue.routingscreen', {})
        
    @http.route('/queue/display/<display_code>/', auth='public')
    def display(self, display_code, **kw):
        env_display = http.request.env['queue.display']
        displays = env_display.sudo().search([('name','=',display_code)])
        display = displays[0]
        env_trans = request.env['queue.trans']
        transs = env_trans.sudo().search([('display_id','=',display.id),('state','=','open')])
        if transs:            
            trans = transs[0]       
            return '{"success":true,"message":"","trans_id": "' +  trans.trans_id + '"}'
        else:
            return '{"success":false,"message":""}'

    @http.route('/queue/routeui/listactive/<display_code>', auth='public')
    def display_list_active(self, display_code):
        queue_pickup_log_obj = http.request.env['queue.pickup.log']
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_type_obj = http.request.env['queue.type']
        queue_trans_obj = http.request.env['queue.trans']
        queue_display_obj = http.request.env['queue.display']

        queue_display_id = queue_display_obj.sudo().search([('name','=', display_code)], limit=1)
        domain = [
            ('display_id', '=', queue_display_id.id)
        ]
        queue_pickup_ids = queue_pickup_obj.sudo().search(domain)
        pickup_list = []
        for queue_pickup_id in queue_pickup_ids:
            domain = [
                ('pickup_id', '=', queue_pickup_id.id),
                ('state', '=', 'opened'),
            ]
            queue_pickup_log_id = queue_pickup_log_obj.sudo().search(domain, limit=1)            
            if queue_pickup_log_id:
                pickup_data = {}
                pickup_data.update({'pickup_name': queue_pickup_id.name})
                pickup_data.update({'counter_name': queue_pickup_id.type_id.name})
                queue_trans_args = [('pickup_id', '=', queue_pickup_id.id), ('state', '=', 'open')]
                queue_trans = queue_trans_obj.sudo().search(queue_trans_args, limit=1, order="create_date desc")
                if queue_trans:
                    pickup_data.update({'current_trans': queue_trans.trans_id})
                else:
                    pickup_data.update({'current_trans': '---'})
                #type_id = queue_type_obj.browse(pickup_id.type_id['id'])
                type_id = queue_pickup_id.type_id
                pickup_data.update({'counter_bg': type_id.bg_color})
                pickup_data.update({'counter_fa': 'fa-users'})
                pickup_data.update({'counter_code': queue_trans.type_id.name})
                pickup_list.append(pickup_data)


        # pickup_log_args = [('state', '=', 'opened')]
        # pickup_list = []
        # pickup_log_ids = queue_pickup_log_obj.search(pickup_log_args)

        # for pickup_log_id in pickup_log_ids:
        #     pickup_id = queue_pickup_obj.browse(pickup_log_id.pickup_id.id)
        #     if pickup_id.display_id.id == display_id:
        #         pickup_data = {}
        #         pickup_data.update({'pickup_name': pickup_id.name})
        #         pickup_data.update({'counter_name': pickup_id.type_id.name})
        #         queue_trans_args = [('pickup_id', '=', pickup_id.id), ('state', '=', 'open')]
        #         queue_trans = queue_trans_obj.search(queue_trans_args, limit=1)
        #         if queue_trans:
        #             pickup_data.update({'current_trans': queue_trans.trans_id})
        #         else:
        #             pickup_data.update({'current_trans': '---'})
        #         type_id = queue_type_obj.browse(pickup_id.type_id['id'])
        #         pickup_data.update({'counter_bg': type_id.bg_color})
        #         pickup_data.update({'counter_fa': 'fa-users'})
        #         pickup_data.update({'counter_code': '0001'})
        #         pickup_list.append(pickup_data)
        return json.dumps(pickup_list)

    @http.route('/queue/routeui/listnew/<display_code>', auth='public')
    def display_list_new(self, display_code):
        queue_type_obj = http.request.env['queue.type']
        queue_trans_obj = http.request.env['queue.trans']
        queue_display_obj = http.request.env['queue.display']

        queue_display_id =  queue_display_obj.sudo().search([('name','=', display_code)], limit=1)
        #queue_type_id = queue_type_obj.sudo().search([('queue_display_id','=',queue_display_id.id)], limit=1)
        #trans_args = [('start_date_time','>', datetime.now().strftime('%Y-%m-%d') + " 00:00:00"),('type_id','=',queue_type_id.id),('state', '=', 'draft')]
        trans_args = [('display_id','=',queue_display_id.id), ('state', '=', 'draft')]
        trans_ids = queue_trans_obj.sudo().search(trans_args, order="write_date")
        trans_list = []
        for trans_id in trans_ids:
            trans_data = {}
            trans_data.update({'counter_name': trans_id.type_id.name})
            trans_data.update({'current_trans': trans_id.trans_id})
            trans_data.update({'counter_fa': 'fa-users'})
            trans_data.update({'counter_code': trans_id.type_id.name})
            trans_data.update({'counter_bg': trans_id.type_id.bg_color})
            trans_list.append(trans_data)
        return json.dumps(trans_list)

    @http.route('/queue/routeui/checksound/<display_code>', auth='public')
    def checksound(self, display_code, **kw):
        queue_type_obj = http.request.env['queue.type']
        queue_trans_obj = http.request.env['queue.trans']
        queue_display_obj = http.request.env['queue.display']

        domain = [
            ('name', '=', display_code)
        ]
        queue_display_id = queue_display_obj.search(domain, limit=1)
        if not queue_display_id:
            return json.dumps({'status': False, 'counter_trans': {}})


        domain = [
            ('iface_recall', '=', True), 
            ('state', '=', 'open'),
            ('display_id', '=', queue_display_id.id)
        ]
        queue_trans_id = queue_trans_obj.sudo().search(domain, order='recall_date_time', limit=1)
        if not queue_trans_id:
            return json.dumps({'status': False, 'counter_trans': {}})
        
        queue_trans_id.iface_recall = False
        return json.dumps({'status': True, 'counter_trans': queue_trans_id.trans_id, 'counter_number': queue_trans_id.pickup_id.name})
      
class Queue_type(http.Controller):
    
    @http.route('/queue/type/listall', auth='public')
    def category_list(self, **kw):
        queue_type = http.request.env['queue.type']
        type_ids = queue_type.sudo().search([])
        types = []
        for type in type_ids:
            type_data = {}
            type_data.update({'counter_id': type.id})
            type_data.update({'counter_name': type.name})
            type_data.update({'counter_bg': type.bg_color})
            type_data.update({'counter_fa': 'fa-users'})
            types.append(type_data)
        return json.dumps(types)

class Queue_app(http.Controller):

    @http.route( ['/queue/kiosk/request/<int:type_id>',
        '/queue/kiosk/request/<int:type_id>/<string:vaccine_type>'], auth='public', csrf=False)
    def app(self, type_id, vaccine_type=None, **kw):

        queue_type_obj = http.request.env['queue.type']
        queue_trans_obj = http.request.env['queue.trans']
        queue_type_id = queue_type_obj.sudo().browse(type_id)
        trans_data = {}
        trans_data.update({'type_id': queue_type_id.id})
        trans_data.update({'display_id': queue_type_id.queue_display_id.id})
        trans_data.update({'vaccine_type': vaccine_type})
        trans = queue_trans_obj.sudo().create(trans_data)
        if not trans:
            return '{"success":false,"message":"Error"}'
        trans_data = {}
        trans_data.update({'trans_id': trans.id})
        trans_data.update({'code': trans.code})
        trans_data.update({'type_id': trans.type_id.id})
        trans_data.update({'counter_name': trans.type_id.name})
        trans_data.update({'counter_trans': trans.trans_id})
        trans_data.update({'counter_bg': trans.type_id.bg_color})
        trans_data.update({'total_count': self.get_total_count(vaccine_type)})
        return json.dumps({"success": True, "data": trans_data})
            

    def get_total_count(self, vaccine_type):
        current_date = datetime.date(datetime.now())
        domain = [
            ('vaccine_type','=', vaccine_type),
            ('trans_date','=', current_date)
        ]

        queue_trans_ids = http.request.env['queue.trans'].sudo().search(domain)
        return len(queue_trans_ids)

    @http.route('/queue/receipt/<int:id>', auth='user')
    def queue_receipt(self, id, **kw):
        queue_trans_obj = http.request.env['queue.trans']
        queue_trans = queue_trans_obj.sudo().browse(id)
        if queue_trans:
            trans_data = {}
            trans_data.update({'counter_trans': queue_trans.trans_id})
            trans_data.update({'counter_type': queue_trans.type_id.name})
            return request.render('jakc_queue.receiptprint', {'data': trans_data})

    @http.route('/queue/kiosk/<kiosk_code>', auth='public')
    def queue_kiosk(self, kiosk_code, **kw):
        domain = [
            ('code', '=', kiosk_code)
        ]
        queue_kiosk =  http.request.env['queue.kiosk'].sudo().search(domain)
        for type in queue_kiosk.queue_type_ids:
            type.mod_bg_color = 'btn3d btn btn-danger btn-lg btn-block'
        return request.render('jakc_queue.kioskscreen', {'types': queue_kiosk.queue_type_ids})
