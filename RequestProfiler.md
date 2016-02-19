

# Integration #

You have to activate the profiler hooks at the very beginning and at the very end of your application's main() function:

```
import lib.profiler.appengine.request

def main():
        lib.profiler.appengine.request.activate()
        run_wsgi_app(application)
        lib.profiler.appengine.request.show_summary()
```

# Profiling information and output #

For sample output, please review the [Wiki screenshots page](http://code.google.com/p/appengine-profiler/wiki/Screenshots#Request_profiler).

Explanation of the fields of each line:
  * **Request summary**:
    * **uptime**: The number of requests this App Engine instance has served. App Engine starts and kills instances dynamically, in order to accommodate the load on your website, and instances are generally persistent for some time.
    * **ID**: Internal request ID. Might be useful if you are debugging something with Google's staff.
    * **Google App Engine/X.Y.Z @ L**: The **X.Y.Z** version of the App Engine, just informative, and the data center location **L** which served your request.
  * **ms** (wall-clock time):
    * the total value in milliseconds - this is what your page took in total to load
    * the usage of each **subsystem** in percents, shown in brackets
  * **cpu\_ms** (CPU time, includes the API CPU time too) - same notation as the "**ms**" line.
  * **api\_cpu\_ms** (CPU time spent by the external systems which you called via the API)  - same notation as the "**ms**" line.

The API calls (to datastore, images, etc.) are automatically accounted by the Request profiler and appear as a **subsystem** in the statistics. The names of these subsystems are prefixed with "**api`_`**". Everything else which was not accounted to any subsystem is being shown as the "**other**" subsystem.

# Tracepoints #

If you want to evaluate the cost of a block in your program, you can enclose code blocks with tracepoints, and thus benchmark their performance.

Every tracepoint must have a unique name, and you cannot have more than one tracepoint activated while another is being active. This prevents that you account a resource twice. Each tracepoint will be accounted as a separate **subsystem** in the **Request summary** (see above). Note that the unique names of your tracepoints should not start with "**api`_`**", as this prefix is used internally.

The [Wiki screenshots page](http://code.google.com/p/appengine-profiler/wiki/Screenshots#Tracepoints) provides a sample output.

An example follows which shows how to create three tracepoints - "loop", "template", and "write":
```
class MainPage(webapp.RequestHandler):
        def get(self, url, hasSlash):
                # ...more code here...

                records = lib.camstore.model.CS_ImageMetaDB.all().filter('uploadTimestamp <', dt_offset).order('-uploadTimestamp').fetch(limit)
                lib.profiler.appengine.request.activate_tracepoint('loop')
                ##
                for imageMeta in records:
                        template_values['images'].append({
                                'camName' : imageMeta.camName,
                                'camAddress' : imageMeta.camAddress,
                                'uploadTimestamp' : naive_dt_astimezone(imageMeta.uploadTimestamp, tzstr).strftime(datefmt),
                                'imageRef' : imageMeta.imageRef,
                        })
                ##
                lib.profiler.appengine.request.deactivate_tracepoint('loop')

                lib.profiler.appengine.request.activate_tracepoint('template')
                ##
                html = template.render('camstore/tpl/index.html', template_values)
                ##
                lib.profiler.appengine.request.deactivate_tracepoint('template')

                lib.profiler.appengine.request.activate_tracepoint('write')
                ##
                self.response.out.write(html)
                ##
                lib.profiler.appengine.request.deactivate_tracepoint('write')
```

Remember that you cannot have a tracepoint active while another is being active. For example, you cannot have a custom tracepoint active and at the same time use an API method (datastore, image, etc) which makes a remote API call. The API calls are automatically accounted by the Request profiler, and internally it uses the same tracepoint mechanism, which will generate a conflict. A "Warning" log entry will be emitted in your logs if such a situation occurs.