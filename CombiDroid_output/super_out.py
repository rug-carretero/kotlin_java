import os
import csv
import logging
import sys
import json
import glob
import pathlib
import subprocess
import traceback
import glob

if __name__ == '__main__':
    
    output_file = pathlib.Path('/.../output_combi_all_kotlin.csv')
    
    total_array = []
    total= ['name','app_package','app_version','app_version_number','app_fingerprint_md5','app_fingerprint_sha1','app_fingerprint_sha256','app_min_sdk_number','app_min_sdk_name','app_min_sdk_version','app_target_sdk_number','app_target_sdk_name','app_target_sdk_version','total_vulnerabilities','num_criticals','num_high','num_med','num_low','num_warnings']
    
    cat = ['Accepting all SSL certificates','Access coarse location permission','Access fine location permission','Allows Backup','Base64 decode','Base64 Encode','Body sensors permission','Call phone permission','Camera permission','Cell Location (Base Stations)','Certificate or Keystore disclosure','Email disclosure','Exported activity','Exported activity-alias','Exported provider','Exported receiver','Exported service','Finally with return statement','Generic Exception in catch','Generic Exception in Throws','Get accounts permission','Get SIM Operator','Get SIM OperatorName','Get SIM Serial','Hardcoded file separator','Internet permission','IP Disclosure','Large heap','Manifest Debug','Math Random method','Process outgoing calls permission','Read calendar permission','Read call log permission','Read contacts permission','Read external storage permission','Read phone state permission','Receive MMS permission','Receive SMS permission','Receive WAP push permission','Record audio permission','Rooted device detection','Send SMS permission','Sending sms-mms','Sleep Method','SQL injection','SSL getInsecure method','Super user privileges.','System command execution','Temp File Use','Unchecked output in Logs','Unknown permission','URL Disclosure','Weak Algorithms','WebView ignores SSL errors','WebView XSS','World readable permissions','Write calendar permission','Write call log permission','Write contacts permission','Write external storage permission','Write secure settings','Write-Read in external storage']
    
    total.extend(cat)
    
    total_array.append(total)
    with open(output_file, "a", newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        try:
            writer.writerows(total_array)
        except Exception as e:
            logging.error(traceback.format_exc())
            print("There was an error with writing to the aggregated csv file")
    
    directory = '/../CombiDroid-parallel/Tools/super/output'
    path = directory + "/*"
    
    loop = 0
    filelist = glob.glob(path)
    for apk_path in sorted(filelist):
        total_array = []
        name = os.path.splitext(os.path.basename(os.path.normpath(apk_path)))[0]
        loop += 1
        if loop >= 0:
            print(name)
            data = None
            path_s = apk_path + "/*"
            
            for filename in glob.glob(path_s):
                if os.path.isdir(filename):
                    filename = os.path.join(filename, "results.json")
                with open(filename, 'r') as f:
                    try:
                        data = json.load(f)
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        data = None
                        continue
                    
            if not data:
                print("There was an error in Super with number: ")
                continue           
               
            app_package = data.get('app_package')
            app_version = data.get('app_version')
            app_version_number = data.get('app_version_number')
            
            app_fingerprint = data.get('app_fingerprint')    
            app_fingerprint_md5 = app_fingerprint['md5']
            app_fingerprint_sha1 = app_fingerprint['sha1']
            app_fingerprint_sha256 = app_fingerprint['sha256']
            
            
            app_min_sdk_number = data.get('app_min_sdk_number')
            app_min_sdk_name = data.get('app_min_sdk_name')
            app_min_sdk_version = data.get('app_min_sdk_version')
            app_target_sdk_number = data.get('app_target_sdk_number')
            app_target_sdk_name = data.get('app_target_sdk_name')
            app_target_sdk_version = data.get('app_target_sdk_version')
            
            total_vulnerabilities = data.get('total_vulnerabilities')
            num_criticals = data.get('criticals_len')
            num_high = data.get('highs_len')
            num_med = data.get('mediums_len')
            num_low = data.get('lows_len')
            num_warnings = data.get('warnings_len')
            
            rules = {}
            for rule in cat:
                rules[rule] = 0
            
            type_array = ['criticals','highs','mediums','lows','warnings']
            for type_x in type_array:
                print(type_x)
                type_vul = data[type_x]    
                for x in range(len(type_vul)):
                    rules[type_vul[x]['name']] += 1 
            
                
            total = []
            total.extend([name,app_package,app_version,app_version_number,app_fingerprint_md5,app_fingerprint_sha1,app_fingerprint_sha256,app_min_sdk_number,app_min_sdk_name,app_min_sdk_version,app_target_sdk_number,app_target_sdk_name,app_target_sdk_version,total_vulnerabilities,num_criticals,num_high,num_med,num_low,num_warnings])
            total.extend(list(rules.values()))
            
            total_array.append(total)
            
            
            with open(output_file, "a", newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                try:
                    writer.writerows(total_array)
                except Exception as e:
                    logging.error(traceback.format_exc())
                    print("There was an error with writing to the aggregated csv file")