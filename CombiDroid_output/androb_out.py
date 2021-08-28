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
     
    output_file_total = pathlib.Path('/../androbugs_total_java_2.csv')
    output_file_rules = pathlib.Path('/../androbugs_rules_java_2.csv')
    
    appNames = []
    records = []
    allines = 0
    cnt = 0
    vulnum = 0
    vulcounter = 0
    vulnerabilities = []
    vulnrecords = []
    vulnapprecords = []
    
    total_array = []
    
    rules = {}
    for x in range(110):
        rules[x] = x
    total = []
    total.extend(['name','pkgname','pkgvname','pkgvcode','minsdk','targetsdk','md5','sha1','sha256','numcritic','numwarn','numnotice','numinfo'])
    total.extend(list(rules.values()))
    
    total_array.append(total)
    with open(output_file_total, "a", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        try:
            writer.writerows(total_array)
        except Exception as e:
            logging.error(traceback.format_exc())
            print("There was an error with writing to the aggregated csv file")

    total_array = []
    
    directory = r'/../CombiDroid-parallel/Tools/androbugs/output'
    path = directory + "/*"
    loop = 0
    filelist = glob.glob(path)
    for apk_path in sorted(filelist):
        freq = {}
        criticals = []
        warnings = []
        notices = []
        info = []
        
        total = []
        
        total_array = []
    
        output_list = glob.glob(apk_path + "/*.txt")
        
        name = os.path.splitext(os.path.basename(os.path.normpath(apk_path)))[0]
        loop += 1
        if loop >= 0:
            if name != 'stdout':
                print(name)
        
                for reportpath in output_list:
                    
                    rules = {}
                    for x in range(110):
                        rules[x] = 0
                    
                    record = []
                    with open(reportpath, encoding='utf-8') as fp:
                        appname = os.path.splitext(os.path.basename(os.path.normpath(reportpath)))[0]
                        line = fp.readline()
                        cnt = 1
                        while line:
                            exists = False
                            if "Package Name: " in line:
                                pkgname = line.replace("Package Name: ", "").strip()
                            if "Package Version Name: " in line:
                                pkgvname = line.replace("Package Version Name: ", "").strip()
                            if "Package Version Code: " in line:
                                pkgvcode = line.replace("Package Version Code: ", "").strip()
                            if "Min Sdk: " in line:
                                minsdk = line.replace("Min Sdk: ", "").strip()
                            if "Target Sdk: " in line:
                                targetsdk = line.replace("Target Sdk: ", "").strip()
                            if "MD5   : " in line:
                                md5 = line.replace("MD5   : ", "").strip()
                            if "SHA1  : " in line:
                                sha1 = line.replace("SHA1  : ", "").strip()
                            if "SHA256: " in line:
                                sha256 = line.replace("SHA256: ", "").strip()
                                
                            serverity = re.search(r"\[(\w+)\]", line)
                            category = re.findall(r"\<(.*?)\>", line)
                            category1 = ""
                            category2 = ""
                            description = ""
                            
                            types_cat = ['Critical','Warning','Info','Notice']
                            
                                
                            if (serverity) and serverity.group(1) in types_cat :
                                if (line not in vulnerabilities):
                                    vulnerabilities.append(line)
                                    vulnum = vulnerabilities.index(line)
                                else:
                                    vulnum = vulnerabilities.index(line)
                                    exists = True
                                serverity = serverity.group(1)
                                if (category):
                                    if (len(category) == 1):
                                        category1 = category[0]
                                        category2 = ""
                                        description = line.replace("[" + serverity + "]", "").replace("<" + category1 + ">",
                                                                                                      "").rstrip().strip(":")
                                    elif (len(category) == 2):
                                        category1 = category[0]
                                        category2 = category[1]
                                        description = line.replace("[" + serverity + "]", "").replace("<" + category1 + ">",
                                                                                                      "").replace(
                                            "<" + category2 + ">", "").rstrip().strip(":")
                                else:
                                    category1 = ""
                                    category2 = ""
                                    description = line.replace("[" + serverity + "]", "").rstrip().strip(":")
                                if not exists:
                                    vulnrecords.append([vulnum, serverity, category1, category2, description])
                                vulnapprecords.append([vulnum, appname, pkgname])
                                
                                add_ssl = 1
                                if category1 == 'SSL_Security':
                                    line = fp.readline()
                                    if "URLs that are NOT under SSL" in line:
                                        ssl_count = line.split(":")
                                        add_ssl = int(ssl_count[1][:-1])                                        
                                rules[vulnum] += add_ssl
                                if serverity in freq:
                                    freq[serverity] += add_ssl
                                else:
                                    freq[serverity] = add_ssl

                            line = fp.readline()
                            cnt += 1
                            
                   
                    print("Package Name: ", pkgname)
                    print("Package Version Name: ", pkgvname)
                    print("Package Version Code: ", pkgvcode)
                    print("Minimum SDK: ", minsdk)
                    print("Tardget SDK: ", targetsdk)
                    print("MD5: ", md5)
                    print("SHA1: ", sha1)
                    print("SHA256: ", sha256)
                    for key, value in freq.items():
                        print("% s : % d" % (key, value))
                    print("-------------------------------------------------------------------------------")

                    if "Critical" in freq:
                        numcritic = freq["Critical"]
                    else:
                        numcritic = 0
                    if "Warning" in freq:
                        numwarn = freq["Warning"]
                    else:
                        numwarn = 0
                    if "Notice" in freq:
                        numnotice = freq["Notice"]
                    else:
                        numnotice = 0
                    if "Info" in freq:
                        numinfo = freq["Info"]
                    else:
                        numinfo = 0
                    
        total.extend([name,pkgname,pkgvname,pkgvcode,minsdk,targetsdk,md5,sha1,sha256,numcritic,numwarn,numnotice,numinfo])
        total.extend(list(rules.values()))
        total_array.append(total)
        freq = {}
                    
    
        with open(output_file_total, "a", newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            try:
                writer.writerows(total_array)
            except Exception as e:
                logging.error(traceback.format_exc())
                print("There was an error with writing to the aggregated csv file")
            
    with open(output_file_rules, "a", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        try:
            writer.writerows(vulnrecords)
        except Exception as e:
            logging.error(traceback.format_exc())
            print("There was an error with writing to the aggregated csv file")