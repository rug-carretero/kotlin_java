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

def parse_subcategory(category, subcategory):
    category1 = "device_settings_harvesting"
    category2 = "suspicious_connection_establishment"
    category3 = "code_execution"
    category4 = "telephony_services_abuse"

    if category == category1:
        match = re.match("This\sapplication\slogs\sthe\smessage", subcategory)
        if match:
            return "Message log"
        elif re.match("This\sapplication\sretrieves", subcategory):
            return "Retrieves certain information"
        else:
            return subcategory
    elif category == category2:
        if re.match("This\sapplication\sopens\sa\sSocket\sand\sconnects\sit\sto\sthe\sremote\saddress", subcategory):
            return "Opens a socket and a connection to remote address"
        else:
            return subcategory
    elif category == category3:
        if re.match("This\sapplication\sloads\sa\snative\slibrary", subcategory):
            return "Loads a native library"
        if re.match("This\sapplication\sexecutes\sa\sUNIX\scommand\scontaining\sthis\sargument", subcategory):
            return "This application executes a UNIX command"
        else:
            return subcategory
    elif category == category4:
        if re.match("This\sapplication\ssends\san\sSMS\smessage", subcategory):
            return "This application sends an SMS message"
        else:
            return subcategory
    else:
        return subcategory

if __name__ == '__main__':
    
    output_file_total = pathlib.Path(r'/../androwarn.csv')
    
    
    total_array = []
    total_head = ['name','app_name','app_version','app_package','md5','sha1','sha256']
    cat = ['code_execution','device_settings_harvesting','suspicious_connection_establishment','PIM_data_leakage','telephony_services_abuse','connection_interfaces_exfiltration','location_lookup','telephony_identifiers_leakage','audio_video_eavesdropping']
    total_head.extend(cat)
     
    rules = {}
    for rule in cat:
        rules[rule] = 0
        
    rules_cat = {}
    
    directory = r'/.../'
    path = directory + "/*"
    loop = 0
    filelist = glob.glob(path)
    
    total_row = []
            
    for apk_path in sorted(filelist):
        name = os.path.splitext(os.path.basename(os.path.normpath(apk_path)))[0]
        loop += 1
        if loop >= 0:
            rules = {}
            for rule in cat:
                rules[rule] = 0
            
            for x in rules_cat:
                rules_cat[x] = 0
            print(name)
            filename = os.path.join('/../CombiDroid-parallel/Tools/androwarn/output/stdout',name)
            filename = pathlib.Path(filename+'.json')
            if os.path.isfile(filename):
                print(filename)
                data = None
                with filename.open('r') as f:
                    try:
                        data = json.load(f)
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        data = None
                        #continue
                        
                if not data:
                    print("There was an error in Super with number: ")
                
                for item in data:
                    if item.get('application_information'):
                        app_info = data[0]['application_information']    
                        app_name = app_info[0][1][0]
                        app_version = app_info[1][1][0]
                        app_package = app_info[2][1][0]
                    if item.get('apk_file'):
                        app_info = data[2]['apk_file']    
                        md5         = app_info[1][1][0]
                        sha1        = app_info[1][1][1]
                        sha256      = app_info[1][1][2]
                    if item.get('analysis_results'):
                        for category in item.get('analysis_results'):
                            for subcategory in category[1]:
                                #print(category[0])
                                #print(subcategory)
                                subcategory = parse_subcategory(category[0], subcategory)
                                #print(category[0])
                                rules[category[0]] += 1
                                if subcategory not in rules_cat:
                                    rules_cat[subcategory] = 1
                                else:
                                    rules_cat[subcategory] += 1
                
                
                total = []
                print(str(sha256[9:]))
                total.extend([str(name),str(app_name),str(app_version),str(app_package),str(md5[5:]),str(sha1[7:]),str(sha256[9:])])
                total.extend(list(rules.values()))
                total.extend(list(rules_cat.values()))
                
                total_row.append(total)
    
    total_head.extend(list(rules_cat))
    total_array.append(total_head)
    
    total_array.extend(total_row)
    with open(output_file_total, "a", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        try:
            writer.writerows(total_array)
        except Exception as e:
            logging.error(traceback.format_exc())
            print("There was an error with writing to the aggregated csv file")
            
        