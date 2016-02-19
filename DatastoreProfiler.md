

# Integration #

You have to activate the profiler hooks at the very beginning and at the very end of your application's main() function:

```
import lib.profiler.appengine.datastore

def main():
        lib.profiler.appengine.datastore.activate()
        run_wsgi_app(application)
        lib.profiler.appengine.datastore.show_summary()
        lib.profiler.appengine.datastore.dump_requests() # optional
```

# Profiling information and output #

## show\_summary() ##

The **show\_summary()** function gives accumulated information about all Datastore requests.

For sample output, please review the [Wiki screenshots page](http://code.google.com/p/appengine-profiler/wiki/Screenshots#Datastore_profiler).

Explanation of the **Datastore API summary** fields follows:
  * **calls**: The total count of remote calls that were made to the API. You should try to keep these to minimum.
  * **ms**: The total amount of wall-clock time in milliseconds which the API calls took.
  * **cpu\_ms**: The total CPU time wasted for serialization/de-serialization of objects and other Datastore-related tasks by the Python SDK. This does not include the API CPU time below.
  * **api\_cpu\_ms**: The total CPU time spent by the Datastore system, which you queried via the API.
  * **entity\_count**: The total count of entities (records) fetched, updated, deleted or otherwise affected by the calls. The speed of the Datastore seems to depend almost linearly on the entities count, so try to keep this to minimum.
  * **kbytes**: The total size of data in KBytes transferred between your application and the Datastore. The speed of the Datastore seems to depend almost linearly on the data size, so try to keep this to minimum.

## dump\_requests() ##

The **dump\_requests()** function provides information about every Datastore request, and its usage is optional. Note that if you have many requests, you will not be able to see all of them in the application log, as it is being automatically truncated by the App Engine.

For sample output, please review the [Wiki screenshots page](http://code.google.com/p/appengine-profiler/wiki/Screenshots#Datastore_profiler).

For each Datastore request you made, two or three lines are output in the log. You can easily see which line belongs to which request, as sub-lines are indented:
  * The **first line** for a request shows the call type (Put, Get, Delete, RunQuery, Next, etc.), and also gives summary information about the call. The summary information is the very same as the one given by [show\_summary()](http://code.google.com/p/appengine-profiler/wiki/DatastoreProfiler#show_summary%28%29) above, only in this case the values reflect only this particular single Datastore request.
  * An optional **second line** line with the "**cost**" may follow. This information is provided internally by the Datastore engine, and is stored in the log without any modifications, apart from re-formatting it on a single line.
  * The **last line** shows the following:
    * **rx/tx** (Receive/Transmit): The size of the data in Bytes (not KBytes) which was transferred between your application and the Datastore for this particular API call.
    * **keys\_only**: Whether the query returned only keys. Queries which return only keys are much faster, as the [documentation about Queries on Keys](http://code.google.com/appengine/docs/python/datastore/queriesandindexes.html#Queries_on_Keys) states.
    * **{'ModelNameA': X, 'ModelNameB': Y}**: The kind of the Models ("ModelNameA" and "ModelNameB") which were involved in the query, and their count ("X" and "Y" respectively).