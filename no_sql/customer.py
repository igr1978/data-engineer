
#!pip install -r requirements.txt

from __future__ import print_function
import aerospike
from aerospike import predicates as p
from aerospike import exception as ex
import sys
import getopt
import pprint
import logging


_client = ''
_namespace = 'test'
_set = 'customers'
_config = {
    'hosts': [('127.0.0.1', 3000)],
    'total_timeout': 1500
}

#_config = {
#    'hosts': [('192.168.99.100', 3000)],
#    'total_timeout': 1500
#}


def add_customer(customer_id, phone_number, lifetime_value):
    key = (_namespace, _set, customer_id)
    try:
        _client.put(key, { 'phone': phone_number, 'ltv': lifetime_value })
    except ex.AerospikeError as e:
        logging.error('error: {0}'.format(e))

def get_ltv_by_id(customer_id):
    key = (_namespace, _set, customer_id)
    try:
        (key, meta, bins) = _client.get(key)
        if bins == {}:
            logging.error('Requested non-existent customer {0}'.format(str(customer_id)))
        else:
            #print('bins: ' + str(bins))
            return bins.get('ltv')
    except ex.AerospikeError as e:
        logging.error('error: {0}'.format(e))

def get_ltv_by_phone(phone_number):
    try:
        query = _client.query(_namespace, _set)
        records  = query.select('phone', 'ltv').where(p.equals('phone', phone_number)).results()
        if len(records) > 0:
            #print(records)
            #print(records[0][2])
            return records[0][2]['ltv']
        else:
            logging.error('Requested phone number is not found {0}'.format(str(phone_number)))
    except ex.AerospikeError as e:
        logging.error('error: {0}'.format(e))
        
def test():
    for i in range(0, 100):
        add_customer(i, i, i + 1)
        logging.info('Test add_customer complete')
    print('Test add_customer complete')

    for i in range(0, 100):
        assert (i + 1 == get_ltv_by_id(i)), "No LTV by ID {0}".format(str(i))
        logging.info('Test get_ltv_by_id complete')
    print('Test get_ltv_by_id complete')    
    
    for i in range(0, 100):
        assert (i + 1 == get_ltv_by_phone(i)), "No LTV by phone {0}".format(str(i))
        logging.info('Test get_ltv_by_phone complete')
    print('Test get_ltv_by_phone complete')

def do_process(arg):
    if len(arg) == 0:
        return

    _customer_id = ''
    _phone_number = ''
    _lifetime_value = ''

    try:
        #add_customer
        if arg[0] == 'add_customer':
            _customer_id = arg[1][0]
            _phone_number = arg[1][1]
            _lifetime_value = arg[1][2]

            add_customer(_customer_id, _phone_number, _lifetime_value)
            #print('add_customer: {0} {1} {2}'.format(_customer_id, _phone_number, _lifetime_value))

        #get_ltv_by_id
        if arg[0] == 'get_ltv_by_id':
            _customer_id = arg[1][0]

            _lifetime_value = get_ltv_by_id(_customer_id)
            #print('get_ltv_by_id: {0} {1}'.format(_customer_id, _lifetime_value))

        #get_ltv_by_phone
        if arg[0] == 'get_ltv_by_phone':
            _phone_number = arg[1][0]

            _lifetime_value = get_ltv_by_phone(_phone_number)
            #print('get_ltv_by_phone: {0} {1}'.format(_phone_number, _lifetime_value))

        #test
        if arg[0] == 'test':
            test()

    except Exception as e:
        logging.error('error: {0} [{1}]'.format(e.msg, e.code))
        sys.exit(1)


def main(argv=None):

    try:
        _client = aerospike.client(_config).connect()
    except ex.AerospikeError as e:
        logging.error('error: {0} [{1}]'.format(e.msg, e.code))
        sys.exit(1)

    try:
        _client.index_integer_create(_namespace, _set, 'phone', 'phone_idx')
    except ex.IndexFoundError as e:
        pass

    if argv is None:
        argv = sys.argv
    try:
        try:
            args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.GetoptError as e:
            print('error: {0} [{1}]'.format(e.msg, e.code))
            sys.exit(2)

        #Arguments
        for arg in args:
            do_process(arg)

    except ex.AerospikeError as e:
        logging.error('error: {0} [{1}]'.format(e.msg, e.code))
        sys.exit(1)
    finally:
        _client.close()


if __name__ == "__main__":
    #main()
    sys.exit(main())
    

#customer.py add_customer 1,2,3
#customer.py get_ltv_by_id 1
#customer.py get_ltv_by_phone 2
#customer.py test
     