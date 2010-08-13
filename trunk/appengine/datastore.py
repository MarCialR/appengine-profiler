from google.appengine.api import apiproxy_stub_map
from google.appengine.datastore import datastore_index
from google.appengine.datastore import datastore_pb
from google.appengine.api import quota
import logging
import lib.profiler.core

# Beware! These are preserved during the whole life of the GAE instance, not just during the life of the request!
# http://code.google.com/appengine/docs/python/runtime.html#App_Caching
requests = None
clock_timer = None
api_timer = None
cpu_timer = None

def _zero_timers(): # for every web request
	global requests
	global clock_timer
	global api_timer
	global cpu_timer
	requests = []
	clock_timer = lib.profiler.core.Timer()
	api_timer = lib.profiler.core.Timer()
	cpu_timer = lib.profiler.core.Timer()

def _log_request(call, kind, keys_only, count, response_ByteSize, request_ByteSize, cost):
	global requests
	global clock_timer
	global api_timer
	global cpu_timer

	if count is None:
		count = -1
	if request_ByteSize is None:
		request_ByteSize = 1
	if response_ByteSize is None:
		response_ByteSize = -1
	if cost is not None:
		cost = str(cost).replace('\n', ', ') + '\n '

	requests.append({
		'call' : call,
		'kind' : kind,
		'keys_only' : keys_only,
		'entities_count' : count,
		'sent_bytes' : request_ByteSize,
		'received_bytes' : response_ByteSize,
		'clock_ms' : clock_timer.get_and_clear() * 1000,
		'api_ms' : quota.megacycles_to_cpu_seconds(api_timer.get_and_clear()) * 1000,
		'cpu_ms' : quota.megacycles_to_cpu_seconds(cpu_timer.get_and_clear()) * 1000,
		'cost' : cost,
	})

def get_summary():
	global requests
	lines = {'call' : 0, 'clock_ms' : 0, 'api_ms' : 0, 'cpu_ms' : 0, 'entities_count' : 0, 'kbytes' : 0}

	for entry in requests:
		for key in lines.keys():
			if key == 'kbytes':
				lines[key] += (entry['received_bytes'] + entry['sent_bytes']) / 1024
			elif key == 'call':
				lines[key] += 1
			else:
				if entry[key] > 0:
					lines[key] += entry[key]
	return lines

def show_summary():
	data = get_summary()
	logging.info('Datastore API summary:\nCalls=%3d, ms=%7.2f, cpu_ms=%7.2f, api_cpu_ms=%7.2f, entity_count=%3d, kbytes=%5.1f' % (
		data['call'], data['clock_ms'], data['cpu_ms'], data['api_ms'], data['entities_count'], data['kbytes']
	))

def dump_requests():
	global requests
	lines = []

	for entry in requests:
		lines.append(
			'%-8s: ms=%7.2f, cpu_ms=%7.2f, api_cpu_ms=%7.2f, entity_count=%3d, kbytes=%5.1f\n  cost=%s rx/tx=%s/%s keys_only=%s %s' % (
			entry['call'],
			entry['clock_ms'], entry['cpu_ms'], entry['api_ms'],
			entry['entities_count'],
			(entry['received_bytes'] + entry['sent_bytes']) / 1024,
			entry['cost'],
			entry['received_bytes'], entry['sent_bytes'],
			entry['keys_only'],
			entry['kind'],
		))
	logging.debug('Datastore API requests:\n' + '\n'.join(lines))

def activate():
	def model_name_from_key(key):
		return key.path().element_list()[0].type()

	def pre_hook(service, call, request, response):
		global clock_timer
		global api_timer
		global cpu_timer
		assert service == 'datastore_v3'
		clock_timer.start()
		api_timer.set_begin(quota.get_request_api_cpu_usage())
		cpu_timer.set_begin(quota.get_request_cpu_usage())

	def post_hook(service, call, request, response):
		global clock_timer
		global api_timer
		global cpu_timer

		assert service == 'datastore_v3'
		clock_timer.stop()
		api_timer.set_end(quota.get_request_api_cpu_usage())
		cpu_timer.set_end(quota.get_request_cpu_usage())

		# http://code.google.com/appengine/docs/python/datastore/functions.html
		if call == 'Put': # you may put different Model kinds in one call
			assert isinstance(request, datastore_pb.PutRequest)
			assert isinstance(response, datastore_pb.PutResponse)
			entity_kinds = {}
			for entity in request.entity_list():
				kind = model_name_from_key(entity.key())
				entity_kinds.setdefault(kind, 0)
				entity_kinds[kind] += 1
			if response.has_cost():
				cost = response.cost()
			else:
				cost = None
			_log_request(call, entity_kinds, None, request.entity_size(), response.ByteSize(), request.ByteSize(), cost)
		elif call == 'Get': # you may get different Model kinds in one call
			assert isinstance(request, datastore_pb.GetRequest)
			assert isinstance(response, datastore_pb.GetResponse)
			entity_kinds = {}
			#for entity in response.entity_list(): # this doesn't work for some reason
			#	kind = model_name_from_key(entity.entity.key)
			#	entity_kinds.setdefault(kind, 0)
			#	entity_kinds[kind] += 1
			for key in request.key_list():
				kind = model_name_from_key(key)
				entity_kinds.setdefault(kind, 0)
				entity_kinds[kind] += 1
			_log_request(call, entity_kinds, None, response.entity_size(), response.ByteSize(), request.ByteSize(), None)
		elif call == 'Delete': # you may delete different Model kinds in one call
			assert isinstance(request, datastore_pb.DeleteRequest)
			assert isinstance(response, datastore_pb.DeleteResponse)
			entity_kinds = {}
			for key in request.key_list():
				kind = model_name_from_key(key)
				entity_kinds.setdefault(kind, 0)
				entity_kinds[kind] += 1
			if response.has_cost():
				cost = response.cost()
			else:
				cost = None
			_log_request(call, entity_kinds, None, request.key_size(), response.ByteSize(), request.ByteSize(), cost)
		elif call == 'RunQuery': # only SELECT/GET queries for one kind?
			assert isinstance(request, datastore_pb.Query)
			assert isinstance(response, datastore_pb.QueryResult)
			if request.has_kind():
				kind = request.kind()
			else:
				# http://code.google.com/appengine/articles/hooks.html
				kind = datastore_index.CompositeIndexForQuery(request)[1] # as seen in the example
			if response.has_keys_only():
				keys_only = response.keys_only()
			else:
				keys_only = None
			_log_request(call, [{kind : 1}], keys_only, response.result_size(), response.ByteSize(), request.ByteSize(), None)
		elif call == 'Next': # used by the SDK internally if you loop over a query
			assert isinstance(request, datastore_pb.NextRequest)
			assert isinstance(response, datastore_pb.QueryResult)
			kind = None
			if response.has_keys_only():
				keys_only = response.keys_only()
			else:
				keys_only = None
			_log_request(call, [{kind : 1}], keys_only, response.result_size(), response.ByteSize(), request.ByteSize(), None)
		else:
			kind = str(request.__class__) + ' : ' + str(response.__class__) + ' : '
			_log_request(call, [{kind : 1}], None, None, None, None, None)

	_zero_timers()
	apiproxy_stub_map.apiproxy.GetPreCallHooks().Push('datastore_profiler', pre_hook, 'datastore_v3')
	apiproxy_stub_map.apiproxy.GetPostCallHooks().Append('datastore_profiler', post_hook, 'datastore_v3')
