import logging
import cProfile, pstats, StringIO

# http://code.google.com/appengine/kb/commontasks.html#profiling

def run(profiled_function, globals_v, locals_v, accumulate_subfunction_calls = False, lines_limit = 20):

	if not profiled_function.endswith('()'):
		raise Exception('The profiled main function name must end with "()", you gave: %s' % (profiled_function))
	if profiled_function == 'main()':
		# You definitely want to rename the original main() function to real_main() and define a new main() function just for the profiler!
		# GAE caches if you have a function named main()
		raise Exception('Do not profile the main() function directly, instead rename it to real_main()');

	prof = cProfile.Profile()
	prof = prof.runctx(profiled_function, globals_v, locals_v)
	stream = StringIO.StringIO()
	stats = pstats.Stats(prof, stream=stream)

	# http://www.python.org/doc//current/library/profile.html?highlight=cprofile#module-pstats
	if accumulate_subfunction_calls:
		# in the stats: 'cumtime'
		# is the total time spent in this and all subfunctions (from invocation till exit). This figure is accurate even for recursive functions
		stats.sort_stats('cumulative')
	else:
		# in the stats: 'tottime'
		# for the total time spent ONLY in the given function (and excluding time made in calls to sub-functions)
		stats.sort_stats('time')

	stats.print_stats(lines_limit)
	logging.debug("cProfile data:\n%s", stream.getvalue())
