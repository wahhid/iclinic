import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import xmlrpclib
from xmlrpclib import Error
import sys

user = 'admin'
pwd = 'P@ssw0rd'
dbname = 'queue_dev_7'
server = 'localhost'
port = '8069'

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
# extensions
auth = HTTPBasicAuth()


class Member():
    
    def __init__(self, customer):
        self.customer = customer
    
    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.customer['id']})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        
        sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
        uid = sock.login(dbname , user , pwd)
        sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')                
        args = [('id','=',data['id'])]            
        ids = sock.execute(dbname, uid, pwd, 'rdm.customer', 'search', args)  
        fields = []
        partner = sock.execute(dbname, uid, pwd, 'rdm.customer', 'read', ids[0], fields)                
        return Member(partner)

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    member = Member.verify_auth_token(username_or_token)
    if not member:
        # try to authenticate with username/password
        sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
        uid = sock.login(dbname , user , pwd)
        sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')                
        args = [('email','=',username_or_token)]            
        ids = sock.execute(dbname, uid, pwd, 'rdm.customer', 'search', args)
        if not ids: 
            return False
        fields= []
        customer = sock.execute(dbname, uid, pwd, 'rdm.customer', 'read', ids[0], fields)
        member = Member(customer)
    g.member = member
    return True

@app.route('/api/v1/login', methods=['GET'])
def login():
    username = request.args.get('username')    
    password = request.args.get('password')
    
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
    uid = sock.login(dbname , user , pwd)
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')                
    args = [('email','=',username),('password','=',password)]            
    ids = sock.execute(dbname, uid, pwd, 'rdm.customer', 'search', args)  
    if not ids:
        #abort(400)
        return jsonify({'success':False,'message':'Error','result':[{}]})
    fields = []
    customer = sock.execute(dbname, uid, pwd, 'rdm.customer', 'read', ids[0], fields)
    member = Member(customer)
    return jsonify({'success':True,'result':[{'username': member.customer['email'],'contact_type':member.customer['contact_type']}]})
    #return '{"username":"' +  member.customer['email'] + '"}'
    
@app.route('/api/users/<int:id>')
def get_user(id):    
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
    uid = sock.login(dbname , user , pwd)
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')                
    args = [('id','=',id)]            
    ids = sock.execute(dbname, uid, pwd, 'res.partner', 'search', args)  
    if not ids:
        abort(400)
    fields = []
    partner = sock.execute(dbname, uid, pwd, 'res.partner', 'read', ids[0], fields)
    return jsonify({'username': partner['email']})

@app.route('/api/v1/token')
@auth.login_required
def get_auth_token():
    token = g.member.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
    
@app.route('/testapi')
def testapi():
    list = [
        {'param':'foo','val':2},
        {'param':'bar','val':10},
    ]    
    return jsonify(results=list)


@app.route('/api/v1/queuedisplay/<name>')
def queue_display(name):    
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
    uid = sock.login(dbname , user , pwd)
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')    
    args = [('name','=', name)]
    ids = sock.execute(dbname, uid, pwd, 'queue.display', 'search', args)    
    if ids:
        id = ids[0]
        args = [('display_id','=',id),('state','=','open')]
        ids = ids = sock.execute(dbname, uid, pwd, 'queue.trans', 'search', args)
        if ids:        
            fields = []            
            data = sock.execute(dbname, uid, pwd, 'queue.trans', 'read', ids, fields)                                 
            return jsonify(success='true',message='',results=data)
        else:
            return jsonify(success='false',message='No Display Found',results=[{}])            
    else:
        return jsonify(success='false',message='No Display Found',results=[{}])
    
@app.route('/api/v1/queuetypelist')
def queue_type_list():
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
    uid = sock.login(dbname , user , pwd)
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')    
    args = []
    ids = sock.execute(dbname, uid, pwd, 'queue.type', 'search', args)  
    if ids:
        fields = []
        data = sock.execute(dbname, uid, pwd, 'queue.type', 'read', ids, fields)                                 
        return jsonify(success='true',message='',results=data)
    else:
        return jsonify(success='false',message='No Type Found',results=[{}])


@app.route('/api/v1/queuepickuplist')
def queue_pickup_list():
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
    uid = sock.login(dbname , user , pwd)
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')    
    args = []
    ids = sock.execute(dbname, uid, pwd, 'queue.pickup', 'search', args)  
    if ids:
        fields = []
        data = sock.execute(dbname, uid, pwd, 'queue.pickup', 'read', ids, fields)                                 
        return jsonify(success='true',message='',results=data)
    else:
        return jsonify(success='false',message='No Type Found',results=[{}])
    
@app.route('/api/v1/app/<int:type_id>')     
def queue_app(type_id):
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
    uid = sock.login(dbname , user , pwd)
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')
    values = {}
    values.update({'type_id': type_id})            
    result = sock.execute(dbname, uid, pwd, 'queue.trans', 'create', values)
    if result:  
        return jsonify(success='true',message='',results=[{}])
    else:
        return jsonify(success='false',message='No Type Found',results=[{}])

@app.route('/api/v1/pickup/<int:type_id>')    
def pickup(type_id):
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port +'/xmlrpc/common')
    uid = sock.login(dbname , user , pwd)
    sock = xmlrpclib.ServerProxy('http://' + server + ':' + port + '/xmlrpc/object')
    args = [('type_id','=', type_id),('state','=','draft')]
    ids =  sock.execute(dbname, uid, pwd, 'queue.trans', 'search', args)
    if ids:
        fields = []
        trans = sock.execute(dbname, uid, pwd, 'queue.trans', 'read', ids[0], fields)        
        values = {}        
        values.update({'state': 'request_pickup'})
        result = sock.execute(dbname, uid, pwd, 'queue.trans', 'write', [trans.id], values)
        if result:
            return jsonify(success='false',message='No Type Found',results=trans)
        else:
            return jsonify(success='false',message='Transaction Error',results=[{}])
    else:
        return jsonify(success='false',message='No Type Found',results=[{}])
    
        
if __name__ == "__main__":
    app.run()