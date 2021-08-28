import os
import sys
import json
import glob
from pathlib import Path
import subprocess

parse_index = 0
  
def parse_argv(argv):
    global parse_index
    result = ''

    while parse_index < len(argv) and argv[parse_index][0] != '-':
        result = result + argv[parse_index]
        parse_index += 1

    return result
    
def parse_input(argv):
    inputdir = ''
    loginSonar = ''
    keySonar = ''
    global parse_index
    
    while parse_index < len(argv):
        opt = argv[parse_index]
        if opt == '-h':
            print('runSonar.py -i <input_dir> -login_sonar <login to localhost sonarqube> -sonar_key <key from portal sonarqube>')
            sys.exit()
        elif opt in ("-i"):
            parse_index += 1
            inputdir = parse_argv(argv)
        elif opt in ("-login_sonar"):
            parse_index += 1
            loginSonar = parse_argv(argv)
        elif opt in ("-sonar_key"):
            parse_index += 1
            keySonar = parse_argv(argv)
        
    return [inputdir,loginSonar,keySonar]
    
def main(argv):
    input_and_output    = parse_input(argv)
    directory           = input_and_output[0]
    login_sonar         = input_and_output[1]
    sonar_key           = input_and_output[2]
    
    print("Checking folder for applications...")
    
    path = directory + "/*"
   
    for apk_path in glob.glob(path):
        name = os.path.splitext(os.path.basename(os.path.normpath(apk_path)))[0]
        print(str(loop)+') '+str(name))
        
        print(directory+name)
        outfile = r"\kotlin\sonar_output_kotlin\/"+name+".txt"
        outfile1 = r"\kotlin\sonar_output_kotlin\/"+name+"_error.txt"
        outfile2 = r"\kotlin\sonar_output_kotlin\/"+name+"_output.txt"
        
        # # delete all projects
        cmd = 'curl -s -u {u} -X POST "http://localhost:9000/api/projects/
            delete?project={n}"'.format(u=login_sonar,n=name)
        result = os.popen(cmd).read()
        with open(outfile, "w+") as file:
            file.write(result)
            
        # # create project
        cmd = 'curl -s -u {} -X POST "http://localhost:9000/api/projects/create?project={}&name={}" '.format(login_sonar,name,name)
        result = os.popen(cmd).read()
        with open(outfile, "w+") as file:
            file.write(result)

        # # run sonarqube analysis
        os.chdir(directory+'/'+name)
        cmd = 'sonar-scanner.bat -D"sonar.projectKey={}" -D"sonar.sources=." -D"sonar.host.url=http://localhost:9000" -D"sonar.login={}" -D"sonar.sourceEncoding=utf-8" -D"sonar.exclusions=**/*.java"'.format(name,sonar_key)
        result = os.popen(cmd).read()
        with open(outfile, "w+") as file:
            file.write(result)
                
        loop += 1        
            
if __name__ == '__main__':
    main(sys.argv[1:])
