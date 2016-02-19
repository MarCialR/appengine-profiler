

# Logs #

The [logs](http://code.google.com/appengine/articles/logging.html) are accessible under the [Administration Console](https://appengine.google.com/) of your App Engine application. They can also be [downloaded via the Python SDK](http://code.google.com/appengine/docs/python/tools/uploadinganapp.html#Downloading_Logs) on your local computer.

# Request profiler #

If you integrate the RequestProfiler in your application, you will get the following profiling details:
```
08-13 12:40AM 04.586 /camstore/upload 200 508ms 351cpu_ms 293api_cpu_ms 0kb libwww-perl/5.825,gzip(gfe)
11.222.111.222 - - [13/Aug/2010:00:40:05 -0700] "POST /camstore/upload HTTP/1.1" 200 181 - "libwww-perl/5.825,gzip(gfe)"
"example.appspot.com:443" ms=508 cpu_ms=352 api_cpu_ms=293 cpm_usd=0.018512

[I] 08-13 12:40AM 05.021
  Request summary (uptime=161, ID=6C0D1DD1:1.999999999 : Google App Engine/1.3.6 @ na5):
  ms         =  425.66 (api_datastore_v3 =  98%, other =   2%)
  cpu_ms     =  326.67 (api_datastore_v3 =  95%, other =   5%)
  api_cpu_ms =  293.33 (api_datastore_v3 = 100%, other =   0%)
```

The meaning of each property is explained in the Wiki documentation page of the RequestProfiler.

## Tracepoints ##

The RequestProfiler gives you the option to also benchmark parts of your code, so that you can identify slow blocks within your application, using Tracepoints:
```
08-12 11:34PM 20.849 /camstore/ 200 1142ms 5540cpu_ms 4412api_cpu_ms 3kb Mozilla/5.0 (X11; U; Linux i686; en-US)
11.222.111.222 - ivan.zahariev.famzah [12/Aug/2010:23:34:21 -0700] "GET /camstore/ HTTP/1.1" 200 3836 "" "Mozilla/5.0 (X11; U; Linux i686; en-US)"
"example.appspot.com" ms=1143 cpu_ms=5540 api_cpu_ms=4412 cpm_usd=0.154410

[I] 08-12 11:34PM 21.884
  Request summary (uptime=73, ID=E1923566:1.999999999 : Google App Engine/1.3.6 @ na5):
  ms         = 1029.13 (api_datastore_v3 =  33%, before_loop =   0%, loop =  13%, template =  32%, write =   0%, other =  22%)
  cpu_ms     = 5879.17 (api_datastore_v3 =  77%, before_loop =   0%, loop =   4%, template =  11%, write =   0%, other =   7%)
  api_cpu_ms = 4412.50 (api_datastore_v3 = 100%, before_loop =   0%, loop =   0%, template =   0%, write =   0%, other =   0%)
```

The subsystem identifiers "before\_loop", "loop", "template", and "write" are tracepoints which we manually defined in the source code, in order to know the resources cost of each block.

The meaning of each property is explained in the Wiki documentation pages of the RequestProfiler.

# Datastore profiler #

If you integrate the DatastoreProfiler in your application, you will get the following profiling details:
```
08-13 12:40AM 04.586 /camstore/upload 200 508ms 351cpu_ms 293api_cpu_ms 0kb libwww-perl/5.825,gzip(gfe)
11.222.111.222 - - [13/Aug/2010:00:40:05 -0700] "POST /camstore/upload HTTP/1.1" 200 181 - "libwww-perl/5.825,gzip(gfe)"
"example.appspot.com:443" ms=508 cpu_ms=352 api_cpu_ms=293 cpm_usd=0.018512

[I] 08-13 12:40AM 05.021
  Datastore API summary:
  Calls=  4, ms= 417.87, cpu_ms=  18.33, api_cpu_ms= 293.33, entity_count=  5, kbytes= 86.0

[D] 08-13 12:40AM 05.022
  Datastore API requests:
  Put     : ms= 189.74, cpu_ms=   4.17, api_cpu_ms=  48.33, entity_count=  1, kbytes= 86.0
    cost=index_writes: 1, index_write_bytes: 1, entity_writes: 1, entity_write_bytes: 89106, 
    rx/tx=55/88892 keys_only=None {'CS_ImageBlobDB': 1}
  Put     : ms=  33.63, cpu_ms=   5.00, api_cpu_ms= 115.00, entity_count=  1, kbytes=  0.0
    cost=index_writes: 9, index_write_bytes: 9, entity_writes: 1, entity_write_bytes: 373, 
    rx/tx=54/158 keys_only=None {'CS_ImageMetaDB': 1}
  RunQuery: ms=  18.60, cpu_ms=   5.00, api_cpu_ms=  21.67, entity_count=  1, kbytes=  0.0
    cost=None rx/tx=496/87 keys_only=0 [{'CS_ImageMetaDB': 1}]
  Delete  : ms= 175.90, cpu_ms=   4.17, api_cpu_ms= 108.33, entity_count=  2, kbytes=  0.0
    cost=index_writes: 10, index_write_bytes: 10, entity_writes: 2, entity_write_bytes: 508, 
    rx/tx=11/86 keys_only=None {'CS_ImageBlobDB': 1, 'CS_ImageMetaDB': 1}
```

The meaning of each property is explained in the Wiki documentation pages of the DatastoreProfiler.

# cProfile profiler #

Additionally to the above profilers, you can also enable the [cProfile](http://docs.python.org/library/profile.html) tool which will give you detailed information about the benchmarks of your Python functions. The idea for this profiler was directly taken from the [Google App Engine documentation](http://code.google.com/appengine/kb/commontasks.html#profiling).

The following screenshot lists only the additional section which is being added (so that we can keep the Wiki page shorter):
```
[D] 08-13 01:05AM 37.010

cProfile data:
         330688 function calls (328272 primitive calls) in 1.185 CPU seconds

   Ordered by: internal time
   List reduced from 515 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1923    0.277    0.000    0.298    0.000 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/template/defaultfilters.py:256(escape)
        1    0.192    0.192    0.257    0.257 {google3.apphosting.runtime._apphosting_runtime___python__apiproxy.Wait}
      481    0.080    0.000    0.081    0.000 {method 'strftime' of 'datetime.date' objects}
      480    0.061    0.000    0.069    0.000 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/template/defaultfilters.py:184(urlencode)
      480    0.030    0.000    0.180    0.000 /base/python_runtime/python_lib/versions/1/google/appengine/api/datastore.py:724(_FromPb)
        1    0.022    0.022    0.053    0.053 {google3.net.proto._net_proto___parse__python.MergeFromString}
     1924    0.017    0.000    0.030    0.000 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/template/__init__.py:617(resolve_variable)
     1920    0.016    0.000    0.029    0.000 /base/python_runtime/python_lib/versions/1/google/appengine/api/datastore_types.py:1558(FromPropertyPb)
        1    0.016    0.016    0.481    0.481 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/template/defaulttags.py:85(render)
     1924    0.013    0.000    0.427    0.000 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/template/__init__.py:561(resolve)
     2403    0.013    0.000    0.384    0.000 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/template/defaultfilters.py:32(_dec)
    12509    0.011    0.000    0.011    0.000 /base/python_runtime/python_lib/versions/1/google/net/proto/ProtocolBuffer.py:196(lengthVarInt64)
    25506    0.011    0.000    0.011    0.000 {isinstance}
      480    0.010    0.000    0.040    0.000 /base/python_runtime/python_lib/versions/1/google/appengine/ext/db/__init__.py:691(__init__)
     1923    0.010    0.000    0.020    0.000 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/utils/html.py:24(escape)
      480    0.009    0.000    0.011    0.000 /base/python_runtime/python_lib/versions/1/google/appengine/ext/db/__init__.py:1199(_load_entity_values)
     1921    0.009    0.000    0.024    0.000 /base/python_runtime/python_lib/versions/1/google/appengine/api/datastore_types.py:1252(ValidateProperty)
      480    0.009    0.000    0.057    0.000 /base/python_runtime/python_lib/versions/1/google/appengine/datastore/entity_pb.py:2156(ByteSize)
     2880    0.009    0.000    0.012    0.000 /base/python_runtime/python_lib/versions/1/google/appengine/api/datastore_types.py:416(id)
     1923    0.009    0.000    0.021    0.000 /base/python_runtime/python_lib/versions/third_party/django-0.96/django/template/__init__.py:753(encode_output)
```

As we can see from the output, the slowest function calls in this case are Django's template engine, the API proxy, and the strftime() method of the 'datetime.date' objects.

The meaning of each property is explained in the Wiki documentation pages of the [cProfileProfiler](cProfileProfiler.md).