Integrating the profiler in your App Engine application will produce logs which show where your application is spending CPU and other resources.

You will get detailed information where your application is being slow, which sections of your code are not optimized and cost you the most, in regards to page response time and billable resources.

You can review the profiler output in the [logs](http://code.google.com/appengine/articles/logging.html) of your application which are accessible in the application's [Administration Console](https://appengine.google.com/). Alternatively you can also download the logs using the Python SDK on your local computer.

The [Wiki](http://code.google.com/p/appengine-profiler/w/list) pages of the project give examples and [screenshots](http://code.google.com/p/appengine-profiler/wiki/Screenshots), and further information.

Currently, the profiler provides statistics about the following App Engine subsystems in a page:
  * [Request summary](http://code.google.com/p/appengine-profiler/wiki/Screenshots#Request_profiler) (_wall-clock response time, CPU/API times, etc_)
  * [Datastore API](http://code.google.com/p/appengine-profiler/wiki/Screenshots#Datastore_profiler)
  * [Python function calls by cProfile](http://code.google.com/p/appengine-profiler/wiki/Screenshots#cProfile_profiler)

The pluggable nature of the implementation allows more subsystems to be added later, and they are in the roadmap of the project:
  * Memcache API
  * Images API
  * Blobstore API
  * URL Fetch API
  * Mail API
  * Task Queues API
  * XMPP API

Your comments and contributions are always welcome.