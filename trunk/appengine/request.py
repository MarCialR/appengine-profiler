from google.appengine.api import quota
from google.appengine.api import apiproxy_stub_map
import logging
import lib.profiler.core
import os

# Beware! These are preserved during the whole life of the GAE instance, not just during the life of the request!
# http://code.google.com/appengine/docs/python/runtime.html#App_Caching
uptime = 0

tracepoints = None # stats per API service
active_tracepoint = None

def _zero_timers(): # for every web request
	global tracepoints
	global active_tracepoint
	tracepoints = {}
	active_tracepoint = None

def activate_tracepoint(name):
	global tracepoints
	global active_tracepoint

	if active_tracepoint is not None:
		logging.warning('Not activating profiling tracepoint "%s" because another tracepoint is active: %s' % (name, active_tracepoint))
		return
	if name != '__other__':
		active_tracepoint = name

	tracepoints.setdefault(name, {
		'clock_usage' : 0,
		'api_usage' : 0,
		'cpu_usage' : 0,
		'clock_timer' : lib.profiler.core.Timer(),
		'api_timer' : lib.profiler.core.Timer(),
		'cpu_timer' : lib.profiler.core.Timer(),
	})
	tracepoints[name]['clock_timer'].start()
	tracepoints[name]['api_timer'].set_begin(quota.get_request_api_cpu_usage())
	tracepoints[name]['cpu_timer'].set_begin(quota.get_request_cpu_usage())

def deactivate_tracepoint(name):
	global tracepoints
	global active_tracepoint

	if name != '__other__':
		if active_tracepoint is None:
			logging.warning(
				'Not deactivating profiling tracepoint "%s" because it was not activated properly' % (
				name
			))
			return
		else:
			if active_tracepoint != name:
				logging.warning(
					'Not deactivating profiling tracepoint "%s" because another tracepoint is active: %s' % (
					name, active_tracepoint
				))
				return
	else:
		if active_tracepoint is not None:
			logging.warning('Profiling end, but the tracepoint "%s" is still active. Forcibly deactivating it!' % (active_tracepoint))
			deactivate_tracepoint(active_tracepoint)

	# if we got here, then it should be safe to deactivate the tracepoint
	if name != '__other__':
		active_tracepoint = None

	tracepoints[name]['clock_timer'].stop()
	tracepoints[name]['api_timer'].set_end(quota.get_request_api_cpu_usage())
	tracepoints[name]['cpu_timer'].set_end(quota.get_request_cpu_usage())
	for t in ('clock', 'api', 'cpu'):
		value = tracepoints[name]['%s_timer' % (t)].get_and_clear()
		tracepoints[name]['%s_usage' % (t)] += value
		if t == 'api':
			tracepoints[name]['cpu_usage'] += value # the API CPU usage is counted towards the total CPU usage too!

def _pre_hook(service, call, request, response):
	activate_tracepoint('api_%s' % (service))

def _post_hook(service, call, request, response):
	deactivate_tracepoint('api_%s' % (service))

def activate():
	initial_cpu_ms = quota.megacycles_to_cpu_seconds(quota.get_request_api_cpu_usage())
	initial_api_ms = quota.megacycles_to_cpu_seconds(quota.get_request_cpu_usage())

	global tracepoints

	_zero_timers()
	activate_tracepoint('__other__')

	if initial_cpu_ms > 1 or initial_api_ms > 1: # we were either not activate()'d at the very beginning, or App Engine did some trick...
		logging.warning('Request profiling: Initial CPU/API counters are not zero: %.1f/%.1f' % (initial_cpu_ms, initial_api_ms))

	apiproxy_stub_map.apiproxy.GetPreCallHooks().Push('request_profiler', _pre_hook)
	apiproxy_stub_map.apiproxy.GetPostCallHooks().Append('request_profiler', _post_hook)

def show_summary():
	global tracepoints
	global uptime

	ms_sub = {
		'clock_ms' : [],
		'api_ms' : [],
		'cpu_ms' : [],
	}
	t_to_visual = {
		'clock_ms' : 'ms',
		'api_ms' : 'api_cpu_ms',
		'cpu_ms' : 'cpu_ms',
	}

	deactivate_tracepoint('__other__') # and populate the statistics for '__other__'
	for subsystem in tracepoints.keys():
		tracepoints[subsystem]['clock_ms'] = tracepoints[subsystem]['clock_usage'] * 1000
		tracepoints[subsystem]['api_ms'] = quota.megacycles_to_cpu_seconds(tracepoints[subsystem]['api_usage']) * 1000
		tracepoints[subsystem]['cpu_ms'] = quota.megacycles_to_cpu_seconds(tracepoints[subsystem]['cpu_usage']) * 1000
	summary_data = tracepoints['__other__']

	subsystems = tracepoints.keys()
	subsystems.sort() # keep the visualize order
	for subsystem in subsystems:
		if subsystem == '__other__':
			continue # this is the total counter
		source_data = tracepoints[subsystem]
		for t in ms_sub.keys():
			if summary_data[t] != 0:
				percentage = (source_data[t] / summary_data[t]) * 100
			else:
				percentage = 0
			ms_sub[t].append((subsystem, percentage))

	line = ''
	fmt = '%s = %3.0f%%'
	for t in ('clock_ms', 'cpu_ms', 'api_ms'): # list to keep the visualize order
		info = []
		total_ms = '%-10s = %7.2f' % (t_to_visual[t], summary_data[t])
		other_percentage = 100
		for subsystem in ms_sub[t]:
			percentage = subsystem[1]
			other_percentage -= percentage
			info.append(fmt % (subsystem[0], percentage))
		info.append(fmt % ('other', other_percentage))
		line += '\n%s (%s)' % (total_ms, ', '.join(info))

	uptime += 1
	logging.info('Request summary (uptime=%d, ID=%s:%s : %s @ %s):%s' % (
		uptime,
		os.environ.get('REQUEST_ID_HASH'), os.environ.get('CURRENT_VERSION_ID'),
		os.environ.get('SERVER_SOFTWARE'), os.environ.get('DATACENTER'),
		line
	))
