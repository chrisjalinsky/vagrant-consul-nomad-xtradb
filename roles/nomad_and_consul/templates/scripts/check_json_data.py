#!/usr/bin/env python
'''A custom Nagios plugin to check data responses in json format.
The need for this plugin was to consume a druid.io json API status page.
A command line arg is present to accept json data string.

Segment Metadata:
=================

./check_json_data.py -H hostname.fqdn.net -p 8083 -d '{"dataSource":"mydata","queryType":"segmentMetadata"}' -u "druid/v2/?pretty" -S "_"

Timeseries Query:
=================

./check_json_data.py -H hostname.fqdn.net -p 8083 -d '{"queryType": "timeseries","dataSource": "mydata","granularity": "all","aggregations":[{"type": "longSum", "fieldName": "myfield", "name": "myitems"}]}' -u "druid/v2/?pretty" -S "myitems"

Datasource Metadata Query:
==========================

./check_json_data.py -H hostname.fqdn.net -p 8083 -d '{"queryType" : "dataSourceMetadata","dataSource": "myitems"}' -u "druid/v2/?pretty" -S "maxIngestedEventTime"


TimeBoundary Query:
===================

./check_json_data.py -H hostname.fqdn.net -p 8083 -d '{"queryType":"timeBoundary","dataSource":"myitems"}' -u "druid/v2/?pretty" -S "result_maxTime"

'''


import json, sys, argparse, requests, datetime, pytz, yaml
    

def create_utc_now(fmt="%Y-%m-%dT%H:%M:%S%z"):
    return datetime.datetime.utcnow().replace(microsecond=0,tzinfo=pytz.utc).strftime(fmt)

def create_utc_time_ago(hrs=2, fmt="%Y-%m-%dT%H:%M:%S%z"):
    dt = datetime.datetime.utcnow() - datetime.timedelta(hours = hrs)
    return dt.replace(microsecond=0,tzinfo=pytz.utc).strftime(fmt)

def create_interval_daterange(check_time):
    return "%s/%s" % (create_utc_time_ago(check_time), create_utc_now())

def compare_dateranges(start_date, end_date, value_date):
    if start_date <= value_date <= end_date:
        return True
    else:
        return False

def create_interval_dict(check_time):
    return { "intervals": [create_interval_daterange(check_time)] }

def post_data(host,port,uri,secure=False,time_out=5,verifyssl=False,postdata={}):

    url = 'https://' if secure else 'http://'
    url += '%s:%s/%s' %(host,port,uri)

    try: 
        response=requests.post(url, verify=verifyssl, timeout=time_out, data=postdata)
    except requests.exceptions.Timeout as e:
        print "Critical: Timeout!"
        sys.exit(2)
    except requests.exceptions.HTTPError as e:
        print "Critical: There was an invalid HTTP response from the server: %s" %e
        sys.exit(2)
    except requests.exceptions.SSLError as e:
        print "Critical: There was an SSL Error response from the server: %s" %e
        sys.exit(2)
    except Exception as e:
        print "Unknown: Something went wrong with the request. %s" %e
        sys.exit(2)

    try:
        urlData = yaml.safe_load(response._content)
    except Exception as e:
        print "Unknown: Something went wrong with %s" %e
        sys.exit(2)

    return urlData

def build_json_data_object(jdata, check_time):
    merge_dicts = dict(create_interval_dict(check_time).items() + jdata.items())
    return json.dumps(merge_dicts)

def flatten(structure, key="", path="", flattened=None):
    if flattened is None:
        flattened = {}
    if type(structure) not in(dict, list):
        flattened[((path + "_") if path else "") + key] = structure
    elif isinstance(structure, list):
        for i, item in enumerate(structure):
            flatten(item, "%d" % i, path + "_" + key, flattened)
    else:
        for new_key, value in structure.items():
            flatten(value, new_key, path + "_" + key, flattened)
    return flattened

def analyze_list_of_objects(data_list, search_string):
    for data_obj in data_list:
        for key in data_obj.keys():
            if search_string in key:
                if data_obj[key] > 0:
                    return True
                else:
                    return False

def compare_posts(warn_post_obj, crit_post_obj, warn_time, crit_time, search_string):
    warning = check_post_response(
        warn_post_obj,
        warn_time,
        crit_time,
        search_string,
    )
    critical = check_post_response(
        warn_post_obj,
        warn_time,
        crit_time,
        search_string,
    )
    if warning and critical:
        if (analyze_list_of_objects(warning, search_string) == True) and (analyze_list_of_objects(critical, search_string) == True):
            print "OK: Both warning and critical time tests pass. There is recent data."
            sys.exit(0)
        elif (analyze_list_of_objects(warning, search_string) == False) and (analyze_list_of_objects(critical, search_string) == True):
            print "Warning: The critical time test passed, but the warning test failed."
            sys.exit(1)
        else:
            print "CRITICAL: The critical test fails. There is no recent data."
            sys.exit(2)
    else:
        print "CRITICAL: The warning and/or critical POST response check for search string key/value pairs failed. A comparison could not be made."
        sys.exit(2)


def check_post_response(data_obj, warn_at, critical_at, search_string):
    #print 'data_obj: %s \r\n' % data_obj
    keys_found = []
    if type(data_obj) in (dict, list):
        if not data_obj:
            print "CRITICAL: The response from Druid is empty."
        else:
              
            dictionary = flatten(data_obj)
            for key in sorted(dictionary.keys()):
                
                if search_string in key:
                    b = { key:dictionary[key] }
                    keys_found.append(b)

            if keys_found:
                print "Keys found. %s" % keys_found
            else:
                print "No Druid records found this POST response."
    else:
        print "The query didn't contain an iterable list. The result was: %s" % data_obj
        
    return keys_found

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Nagios Druid JSON Memory Check Plugin")
    
    parser.add_argument('-H', '--host',
        dest='hostname',
        action="store",
        default='localhost',
        required=False,
        help='optional hostname to connect to. Defaults to localhost',
    )

    parser.add_argument('-p', '--port',
        dest='port',
        action="store",
        default=8080,
        required=False,
        help='optional port of the check. Defaults to 8080',
    )

    parser.add_argument('-u', '--uri',
        dest='uri',
        action="store",
        default='status',
        required=False,
        help='optional URI of the check. Defaults to "status"',
    )

    parser.add_argument('-t', '--timeout',
        dest='timeout',
        action="store",
        default=5,
        required=False,
        type=float,
        help='An optional timeout in seconds. Defaults to 5',
    )

    parser.add_argument('-s', '--secure',
        dest='secure',
        action="store_true",
        default=False,
        required=False,
        help='An optional flag to use secure HTTP.',
    )

    parser.add_argument('-v', '--verify-ssl',
        dest='verifyssl',
        action="store_true",
        default=False,
        help='An optional timeout in seconds which defaults to 5. Must be used with the -s flag.',
    )

    parser.add_argument('-d', '--data',
        dest='jdata',
        action='store',
        default=json.loads('{}'),
        type=json.loads,
        required=False,
        help='Pass json data to the post request. You must use a literal string, and wrap key/value pairs in double-quotes. For example, -d \'{"key":"value"}\'. Defaults to "{}"',
    )

    parser.add_argument('-S', '--search-string',
        dest='sstring',
        action='store',
        default='',
        required=True,
        help='This is an required parameter. It is a string to search for in the flattened dictionary of key/values that get created.',
    )

    parser.add_argument('-n','--unit-size',
        dest='unit_size',
        default='GB',
        required=False,
        help='Optional unit of measure. Defaults to GB',
    )

    parser.add_argument('-w','--warning-time',
        dest='warn_time',
        default=2,
        type=float,
        required=False,
        help='Optionally change the warning time period in hrs. Defaults to 2.',
    )

    parser.add_argument('-c','--critical-time',
        dest='crit_time',
        default=3,
        type=float,
        required=False,
        help='Optionally change the critical time period in hrs. Defaults to 3.',
    )
    
    arg_obj=parser.parse_args()
    
    if arg_obj.secure == False and arg_obj.verifyssl == True:
        print "Critical. Arguments error. -s and -v must be used together."
        sys.exit(2)
    
    warn_json_data=build_json_data_object(arg_obj.jdata, arg_obj.warn_time)
    print 'warn_json_data: %s \r\n' % warn_json_data
    
    crit_json_data=build_json_data_object(arg_obj.jdata, arg_obj.crit_time)
    print 'crit_json_data: %s \r\n' % crit_json_data
    
    if warn_json_data:
        warn_post=post_data(
            arg_obj.hostname,
            arg_obj.port,
            arg_obj.uri,
            arg_obj.secure,
            arg_obj.timeout,
            arg_obj.verifyssl,
            warn_json_data,
        )
    else:
        print "CRITICAL: Could not construct the JSON obj for the warning REST call to Druid."
        sys.exit(2)
    
    if crit_json_data:
        crit_post=post_data(
            arg_obj.hostname,
            arg_obj.port,
            arg_obj.uri,
            arg_obj.secure,
            arg_obj.timeout,
            arg_obj.verifyssl,
            crit_json_data,
        )
    else:
        print "CRITICAL: Could not construct the JSON obj for the critical REST call to Druid."
        sys.exit(2)
    
    if warn_post and crit_post:
        compare_posts(
            warn_post,
            crit_post,
            arg_obj.warn_time,
            arg_obj.crit_time,
            arg_obj.sstring,
        )
    else:
        print "CRITICAL: Either the warning POST and/or critical POST to Druid failed. Could not compare the two."
        sys.exit(2)