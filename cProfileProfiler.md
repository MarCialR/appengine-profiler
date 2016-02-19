

# Initial source #

The idea for this profiler was borrowed from the [Google App Engine documentation](http://code.google.com/appengine/kb/commontasks.html#profiling). We just packed it and tried to make it even a bit more easier to use.

# Integration #

To activate this profiler, first rename your application's **main()** function to **real\_main()**. Then, add a new **main()** function to your application:
```
import lib.profiler.cprofile

def real_main():
        run_wsgi_app(application)

# You definitely want to rename the original main() function to real_main() and define a new main() function just for the profiler!
def main():
        lib.profiler.cprofile.run('real_main()', globals(), locals())
```

If you want to disable the profiler temporarily, you can modify your new main() function as follows:
```
def real_main():
        run_wsgi_app(application)

def main():
        #lib.profiler.cprofile.run('real_main()', globals(), locals())
        real_main()
```

Note that you definitely want to rename the original main() function to real\_main() and define a new main() function just for the profiler. App Engine caches if you have a function named main(), and you will get in trouble if you do not follow this renaming rule.

## Optional arguments ##

There are some optional named arguments which you can pass to the **run()** function:
  * **accumulate\_subfunction\_calls** (default is False): Affects the [sort\_stats()](http://www.python.org/doc//current/library/profile.html?highlight=cprofile#pstats.Stats.sort_stats) order of cProfile. True makes it 'cumulative' (usually not very useful), False makes it 'time'.
  * **lines\_limit** (default is 20): Affects how many lines will be output at most.

# Profiling information and output #

For sample output, please review the [Wiki screenshots page](http://code.google.com/p/appengine-profiler/wiki/Screenshots#cProfile_profiler).

The output is directly taken from the [Python cProfile module](http://www.python.org/doc//current/library/profile.html?highlight=cprofile#module-pstats), and therefore there is no need to duplicate the documentation here.