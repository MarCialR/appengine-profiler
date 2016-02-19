

There is no problem to use multiple profilers simultaneously. Here is an example which shows how to activate both the RequestProfiler and the DatastoreProfiler for a page:

```
import lib.profiler.appengine.request
import lib.profiler.appengine.datastore

def main():
        lib.profiler.appengine.request.activate()
        lib.profiler.appengine.datastore.activate()

        run_wsgi_app(application)

        lib.profiler.appengine.request.show_summary()
        lib.profiler.appengine.datastore.show_summary()
        lib.profiler.appengine.datastore.dump_requests() # optional
```