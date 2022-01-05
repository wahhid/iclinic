# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,Controller, route
import json
from openerp.tools.translate import _
from odoo.addons.jakc_queue.controllers.controllers import Queue_app as QA
from odoo.addons.jakc_queue.controllers.controllers import QueuePickup as QP
from datetime import datetime


import logging
_logger = logging.getLogger(__name__)

class QueueAppInherit(QA):

    @http.route( ['/queue/kiosk/request/<int:type_id>',
        '/queue/kiosk/request/<int:type_id>/<string:vaccine_type>'], auth='public', csrf=False)
    def app(self, type_id, vaccine_type=None, **kw):
        #res = super(QueueAppInherit,self).app(type_id, vaccine_type=None, **kw)
        _logger.info("Queue App Inherit")
        queue_type_obj = http.request.env['queue.type']
        queue_trans_obj = http.request.env['queue.trans']
        queue_type_id = queue_type_obj.sudo().browse(type_id)
        trans_data = {}
        trans_data.update({'type_id': queue_type_id.id})
        trans_data.update({'display_id': queue_type_id.queue_display_id.id})
        trans_data.update({'vaccine_type': vaccine_type})
        trans_data.update({'operating_unit_id': queue_type_id.operating_unit_id.id})
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
        trans_data.update({'operating_unit_id': trans.operating_unit_id.id})
        _logger.info(trans_data)
        return json.dumps({"success": True, "data": trans_data})
        # return res



class QueuePickup(QP):

    @http.route('/queue/pickup/<int:id>/', auth='public')
    def pickup(self, id):
        _logger.info("Queue Pikcup Inherit")
        queue_pickup_obj = http.request.env['queue.pickup']
        queue_pickup_log_obj = http.request.env['queue.pickup.log']
        queue_trans_obj = http.request.env['queue.trans']
        pickup = queue_pickup_obj.browse(id)
        if pickup:
            trans_args = [
                ('trans_date','=', datetime.now().strftime('%Y-%m-%d')),
                ('state', '=', 'draft'), 
                ('type_id', '=', pickup.type_id.id),
                ('operating_unit_id','=', pickup.operating_unit_id.id)
            ]
            _logger.info(trans_args)
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

    @http.route('/queue/finish/<int:id>/', auth='public')
    def finish(self, id):
        queue_trans_obj = http.request.env['queue.trans']
        queue_trans_id = queue_trans_obj.browse(id)
        if not queue_trans_id:
            return json.dumps({'status': False})
        
        if queue_trans_id.type_id.next_type_id:
            queue_trans_id.next_type_id = queue_trans_id.type_id.next_type_id.id
            return json.dumps({'status': True})
            
        if queue_trans_id.state == 'open':
            queue_trans_id.write({'end_date_time': datetime.now(), 'state': 'done'})
            return json.dumps({'status': True})
    
        # if trans.state != 'done':
        #     trans.write({'pickup_id': False})   
        # else:
        #     trans.write({'end_date_time': datetime.now(), 'state': 'done'})
        return json.dumps({'status': False})