import os
import csv
import logging
import sys
import json
import glob
import pathlib
import subprocess
import traceback
import re


if __name__ == '__main__':
    output_file_total = pathlib.Path(r'/../flow_kotlin.csv')
    
    array_source = ['android.util.Log','android.os.Bundle','android.content.Context','android.content.Intent','android.app.Activity','java.io.OutputStream','java.io.ByteArrayOutputStream','java.io.Writer','androidx.activity.ComponentActivity','android.content.SharedPreferences$Editor','java.net.HttpURLConnection','java.lang.String','android.support.v4.app.l','androidx.fragment.app.FragmentActivity','android.content.ContentResolver','java.io.File','android.content.IntentFilter','android.app.Service','java.io.PrintWriter','java.io.OutputStreamWriter','java.io.FileOutputStream','androidx.core.app.ComponentActivity','java.io.FileWriter','java.io.BufferedWriter','android.os.Handler','java.net.URL','androidx.core.app.d','androidx.core.app.c']
    sink_cat_array = ['android.util.Log', 'android.os.Bundle', 'android.content.Context', 'android.content.Intent', 'android.app.Activity', 'java.io.OutputStream', 'java.io.ByteArrayOutputStream', 'java.io.Writer', 'androidx.activity.ComponentActivity', 'android.content.SharedPreferences$Editor', 'java.net.HttpURLConnection', 'java.lang.String', 'android.support.v4.app.l', 'androidx.fragment.app.FragmentActivity', 'android.content.ContentResolver', 'java.io.File', 'android.content.IntentFilter', 'android.app.Service', 'java.io.PrintWriter', 'java.io.OutputStreamWriter', 'java.io.FileOutputStream', 'androidx.core.app.ComponentActivity', 'java.io.FileWriter', 'java.io.BufferedWriter', 'android.os.Handler', 'java.net.URL', 'androidx.core.app.d', 'androidx.core.app.c']
    
    
    source_cat_array = ['android.location.Location', 'android.database.Cursor', 'java.net.URL', 'java.net.HttpURLConnection', 'android.content.pm.PackageManager', 'io.github.benoitduffez.cupsprint.app.AddPrintersActivity', 'javax.net.ssl.HttpsURLConnection', 'java.util.Locale', 'android.location.LocationManager', 'android.bluetooth.BluetoothAdapter', 'android.support.v7.app.AppCompatActivity', 'org.apache.http.HttpResponse', 'java.net.URLConnection', 'android.content.ContentResolver', 'android.database.CursorWrapper', 'android.accounts.AccountManager', 'android.telephony.TelephonyManager','android.net.wifi.WifiInfo','org.apache.http.util.EntityUtils','org.jsoup.parser.Parser','android.media.AudioRecord','android.app.Activity','java.util.Calendar','android.telephony.gsm.GsmCellLocation']
    source_cat = {}
    sink_cat = {}
    
    total_array = []
    
    directory = r'/../'
    path = directory + "/*"
    loop = 0
    filelist = glob.glob(path)
    total_row = []
    for apk_path in sorted(filelist):
        loop += 1
        if loop > 0:
            name = os.path.splitext(os.path.basename(os.path.normpath(apk_path)))[0]
            print(apk_path)
            
            for x in source_cat_array:
                source_cat[x] = 0
            for x in sink_cat_array:
                sink_cat[x] = 0                
            
            print(source_cat)
            
            with open(apk_path) as fp:
                line = fp.readline()
            
                while line:
                    
                    match = re.search("The\ssink\s", line)
                    if match:
                        sink_invoke = re.search("<[\w\W]+?:", line)
                        print(sink_invoke.group()[1:-1])
                        sink = None
                        if sink_invoke.group()[1:-1] in array_source:
                            sink_cat[sink_invoke.group()[1:-1]] += 1     
                        else:
                            sink_invoke = re.search("\([\w\W]+?,", line)
                            if not sink_invoke:
                                sink_invoke = re.search("\([\w\W]+?\)", line)
                            if sink_invoke.group()[1:-1] not in array_source:
                                sink_invoke = re.search("android.content.Intent", line)
                            if sink_invoke:
                                sink = sink_invoke.group()[1:-1]
                            #else:
                                #input("..")
                            if sink == 'ndroid.content.Inten' or sink == 'Android.content.Intent':
                                sink = 'android.content.Intent'
                            print("Test: {}".format(sink))
                            if sink:
                                sink_cat[sink] += 1
                            
                            #input("..")
                        
                        line = fp.readline()
                        while not re.search("The\ssink\s", line):
                            sources = re.findall("<[\w\W]+?>", line)
                            if not sources:
                                break
                            source_invoke = sources[0]
                            source_invoke2 = re.search("<[\w\W]+?:", source_invoke)
                            print(source_invoke2.group()[1:-1])
                            if source_invoke2.group()[1:-1] in source_cat:
                                source_cat[source_invoke2.group()[1:-1]] += 1
                            
                            line = fp.readline()
                    else:
                        previous_line = line
                        line = fp.readline()
                    if not line:
                        number_of_leaks = 0
                        number_of_leaks_line = re.search("Found\s\d+\sleaks", previous_line)
                        if not number_of_leaks_line:
                            print("FAIL")
                            continue
                        number_of_leaks = re.search("\d+", number_of_leaks_line.group()).group()
                        
            print(number_of_leaks)
            total = []
            total.extend([name,number_of_leaks])
            total.extend(list(sink_cat.values()))
            total.extend(list(source_cat.values()))
            total_row.append(total)
    
    total_head = ['name','number_of_leaks']
    total_head.extend(list(sink_cat))
    total_head.extend(list(source_cat))
    
    total_array.append(total_head)
    total_array.extend(total_row)
    
    print(total_array)
    
    print(sink_cat)
    print(source_cat)
    
    print(list(sink_cat))
    print(list(source_cat))
    
    
    with open(output_file_total, "a", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        try:
            writer.writerows(total_array)
        except Exception as e:
            logging.error(traceback.format_exc())
            print("There was an error with writing to the aggregated csv file")