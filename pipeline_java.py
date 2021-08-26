import glob, os, subprocess, re
import pathlib

cwd = os.getcwd()
                        
def search_string_in_file(file_name, string_to_search):
    line_number = 0
    list_of_results = []
    with open(file_name, 'r') as read_obj:
        for line in read_obj:
            line_number += 1
            if string_to_search in line:
                list_of_results.append((line_number, line.rstrip()))
    return list_of_results

def get_build_file(path):
    folders = os.listdir(path)
    if folders:
        path_gradle = path+"/"+folders[0]+"/build.gradle"
        path_maven = path+"/"+folders[0]+"/pom.xml"
        if os.path.exists(path_gradle):
            return 'gradle'
        if os.path.exists(path_maven):
            return 'mvn'            
    return None

def create_local_properties(path_local):
    with open(path_local, "w") as file:
        file.write("sdk.dir=/android-sdk-linux\nsdk-location=/android-sdk-linux")
    return 1

def set_android_sdk(path):
    folders = os.listdir(path)
    if folders:
        path_gradle = path+"/"+folders[0]+"/local.properties"
        if os.path.exists(path_gradle):
            os.remove(path_gradle)
            return create_local_properties(path_gradle)
        else:
            return create_local_properties(path_gradle)
    return None

def get_gradle_version(path):
    folders = os.listdir(path)
    if folders:
        path_gradle = path+"/"+folders[0]+"/gradle/wrapper/gradle-wrapper.properties"
        if os.path.exists(path_gradle):
            matched_lines = search_string_in_file(path_gradle, 'distributionUrl')
            for elem in matched_lines:
                return elem[1]
        else:
            return None
    return None

def set_gradle_version(gradle_url):
    url = gradle_url.rsplit('/', 1)[-1]
    version = url.rsplit('-', 1)[0]
    
    path = "/opt/gradle/{}".format(version)
    if not os.path.exists(path):
        wget_url = gradle_url.rsplit('=', 1)[-1]
        print(wget_url)
        
        path_download = '/tmp/{}'.format(url)
        print(path_download)
        # download gradle version
        if os.path.exists(path_download):
            os.remove(path_download)
        cmd = 'wget {} -P /tmp'.format(wget_url)
        result = os.popen(cmd).read()
        
        #unzip zip file
        cmd = 'sudo unzip -d /opt/gradle /tmp/{}'.format(url)
        result = os.popen(cmd).read()
    
    new_path = os.environ["PATH"]
    gradle_home = '/opt/gradle/{}/bin'.format(version)
    if not re.match(gradle_home,new_path):
        os.environ["PATH"] = '{}:{}'.format(gradle_home,new_path)
    return 1
    
def update_build_file(path):
    folders = os.listdir(path)
    if folders:
        filename = path+"/"+folders[0]+"/build.gradle"
        
        size = os.path.getsize(filename)
        
        if size > 0:
            sonar_found = 0
            lookup = 'id "org.sonarqube" version "3.0"'
            with open(filename) as myFile:
                for num, line in enumerate(myFile, 1):
                    line_s = line.rstrip()
                    if lookup in line:
                        sonar_found = num
            if sonar_found > 0:
                return 1
            if sonar_found == 0:
                plugins_found = 0
                lookup = 'plugins {'
                with open(filename) as myFile:
                    for num, line in enumerate(myFile, 1):
                        line_s = line.rstrip()
                        if lookup in line:
                            plugins_found = num
                
                if plugins_found == 0:
                    line_f = 0
                    insert_line = 0
                    lookup = 'buildscript {'
                    
                    with open(filename) as myFile:
                        for num, line in enumerate(myFile, 1):
                            line_s = line.rstrip()
                            if lookup in line:
                                line_f = num
                    with open(filename) as myFile:
                        for num, line in enumerate(myFile, 1):
                            line_s = line.rstrip()
                            if num > line_f:
                                if not re.match(r'\s', line) and line_s == '}':
                                    insert_line = num
                                    break
                                    
                    with open(filename, "r") as f:
                        lines = f.readlines()

                        for index, line in enumerate(lines):
                            if index == insert_line:
                                break
                        lines.insert(index, "}\n")
                        lines.insert(index, '   id "org.sonarqube" version "3.0"\n')
                        lines.insert(index, "plugins {\n")
                        
                        with open(filename, "w") as f:
                            contents = f.writelines(lines)
                        return 1
                else:
                    with open(filename, "r") as f:
                        lines = f.readlines()

                        for index, line in enumerate(lines):
                            if index == plugins_found:
                                break
                        lines.insert(index, '   id "org.sonarqube" version "3.0"\n')
                        
                        with open(filename, "w") as f:
                            contents = f.writelines(lines)
                        return 1
    return 0
    
def rm_tree(pth):
    pth = pathlib.Path(pth)
    for child in pth.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()

def new_names(foldername):
    foldername_new = (re.sub('\s+', '_', foldername))
    foldername_new = (re.sub('[^a-zA-Z0-9._-]', '_',  foldername_new))
    foldername_new = re.sub('_+', '_', foldername_new)
    return foldername_new
  
def perform_analysis(path,name,login_sonar):
    os.chdir(path)
                        
    outfile = cwd + "/output/apps/"+str(name)+".txt"
    print(outfile)
    #Stop gradle deamon
    execute_cmd = 'gradle --stop'
    with open(outfile, 'a') as f_out:
        p = subprocess.Popen(execute_cmd, shell=True, stdout=f_out, stderr=subprocess.STDOUT)
    (output, err) = p.communicate()  
    p_status = p.wait()
    
    #delete project if exists
    print("Delete project from SonarQube")
    execute_cmd = 'curl -s -u {u} -X POST "http://host.docker.internal:9000/api/projects/delete?project={n}"'
        .format(u=login_sonar,n=name)
    with open(outfile, 'a') as f_out:
        p = subprocess.Popen(execute_cmd, shell=True, stdout=f_out, stderr=subprocess.STDOUT)
    (output, err) = p.communicate()  
    p_status = p.wait()
    
    #create project
    print("Create project")
    execute_cmd = 'curl -s -u {} -X POST "http://host.docker.internal:9000/api/projects/create?project={}&name={}" '.format(login_sonar,name,name)
    p = subprocess.Popen(execute_cmd, shell=True)
    (output, err) = p.communicate()  
    p_status = p.wait()
    
    
    #perform analysis
    print("Analysis with SonarQube")
    execute_cmd = 'gradle sonarqube -D "sonar.projectKey={}" -D "sonar.host.url=http://host.docker.internal:9000" -D "sonar.login=865d114debfa5078f0654e64a2d9ffeacb4aa1b8"'.format(name)
    with open(outfile, 'a') as f_out:
        p = subprocess.Popen(execute_cmd, shell=True, stdout=f_out, stderr=subprocess.STDOUT)
    (output, err) = p.communicate()  
    p_status = p.wait()
    
    #Stop gradle deamon
    execute_cmd = 'gradle --stop'
    with open(outfile, 'a') as f_out:
        p = subprocess.Popen(execute_cmd, shell=True, stdout=f_out, stderr=subprocess.STDOUT)
    (output, err) = p.communicate()  
    p_status = p.wait()

def word_in_file(filename, name):
    with open(filename, 'r') as f:
        for line in f:
            if name in line:
                return True
        return False

if __name__ == '__main__':
    total_count = 0

    login_sonar = 'LOGIN:PASSWORD'

    directory = "/home/data/source_unzipped"
    path = directory + "/*"
    
    path_output = pathlib.Path(cwd + "/output/")
    for source_path in glob.glob(path):
        name = os.path.splitext(os.path.basename(os.path.normpath(source_path)))[0]
            
        name_original = name
        name = new_names(name)
        proces_check_1 = word_in_file("/home/data/completed_application_parsing.txt",name)
        proces_check_2 = word_in_file("/home/data/failed_application_parsing.txt",name)
        print(str(total_count) +") "+str(name))
        
        if proces_check_1 or proces_check_2:
            print("allready analyzed")
        else:
            if total_count >= 0:
                print(str(total_count) +") "+str(name))            
            
                # check build file in root directory
                build_file = get_build_file(source_path)
                
                if build_file == 'gradle':
                    # set local.properties with correct ANDROID sdk location
                    android_sdk = set_android_sdk(source_path)
                    
                    # get gradle version from /gradle/wrapper/
                    gradle_version = get_gradle_version(source_path)
                    
                    if not gradle_version:
                        #start deamon to see version, does not work in all cases. 
                        print("Check gradle version")
                        execute_cmd = 'gradle --daemon'
                        execute_cmd = 'gradle --daemon'
                        outfile = cwd + "/output/apps/"+str(name)+"_gradle_version.txt"
                        with open(outfile, 'a') as f_out:
                            p = subprocess.Popen(execute_cmd, shell=True, stdout=f_out, stderr=subprocess.STDOUT)
                        (output, err) = p.communicate()  
                        p_status = p.wait()
                        
                        matched_lines = search_string_in_file(outfile, 'Welcome to Gradle')
                        string_from_file = '' 
                        for elem in matched_lines:
                            string_from_file = elem[1]
                            break
                            
                        result = re.search('Welcome to Gradle (.*).', string_from_file)
                        if result:
                            gradle_version = 'https\://services.gradle.org/distributions/gradle-{}-all.zip'.
                                format(result.group(1))
                        
                        if not string_from_file:
                            matched_lines = search_string_in_file(outfile, 'Gradle version ')
                            for elem in matched_lines:
                                string_from_file = elem[1]
                                break                                
                            
                            result = re.search('Gradle version (.*) is required', string_from_file)
                            if result:
                                gradle_version = 'https\://services.gradle.org/distributions/
                                    gradle-{}-all.zip'.                                    format(result.group(1))

                    if gradle_version:
                        # check if gradle version exists, if not download and extract
                        # update environments settings
                        set_gradle_version(gradle_version)
                        
                        # add sonarqube task to build.gradle
                        build_update = update_build_file(source_path)
                        if build_update == 1:
                            folders = os.listdir(source_path)
                            if folders:
                                change_path = source_path+'/'+folders[0]
                                
                                #perform analysis
                                perform_analysis(change_path,name,login_sonar) 
                            
                                #location output file
                                outfile = cwd + "/output/apps/"+str(name)+".txt"
            
                                #sometime sonarqube docker images quits due to memory. Check if sonarqube task failed, if so check if docker image is still running
                                matched_lines = search_string_in_file(outfile, 'Task :sonarqube FAILED')
                                matched_lines_2 = search_string_in_file(outfile, 'Unable to execute SonarScanner analysis')
                                if matched_lines or matched_lines_2:
                                    print("Docker down")
                                    print('....')
                                    #input('Press any key to continue..')
                                
                                #wrong gradle version, try again will gradle verion mentioned in output file. 
                                matched_lines = search_string_in_file(outfile, "Failed to apply plugin [id 'com.android.application']")
                                if matched_lines:
                                    matched_lines = search_string_in_file(outfile, 'Gradle version ')
                                    string_from_file = '' 
                                    for elem in matched_lines:
                                        string_from_file = elem[1]
                                        break                                        
                                    
                                    result = re.search('Gradle version (.*) is required', string_from_file)
                                    if result:
                                        gradle_version = 'https\://services.gradle.org/distributions/
                                            gradle-{}-all.zip'.
                                            format(result.group(1))
                                        print(gradle_version)
                                        
                                        # set environments
                                        set_gradle_version(gradle_version)
                        
                                        # add sonarqube task to build.gradle
                                        build_update = update_build_file(source_path)
                                        
                                        #perform analysis
                                        perform_analysis(change_path,name,login_sonar) 
                                
                                finish = 0
                                #check if build is successfull
                                completed_file = cwd + '/completed_application_parsing.txt'
                                matched_lines_success = search_string_in_file(outfile, 'BUILD SUCCESSFUL')
                                if matched_lines_success:
                                    print("Successful analysis")
                                    finish = 1
                                    with open(completed_file, 'a') as f:
                                        f.write(str(name_original) +','+ str(name) + '\n') 
                    
                                #check if build failed
                                failed_file = cwd + '/failed_application_parsing.txt'
                                matched_lines = search_string_in_file(outfile, 'BUILD FAILED')
                                if matched_lines and finish == 0:
                                    print("Failed analysis")
                                    print("Delete project from SonarQube")
                                    execute_cmd = 'curl -s -u {u} -X POST "http://host.docker.internal:9000/api/projects/
                                        delete?project={n}"'.
                                        format(u=login_sonar,n=name)
                                    with open(outfile, 'a') as f_out:
                                        p = subprocess.Popen(execute_cmd, shell=True, stdout=f_out, stderr=subprocess.STDOUT)
                                    (output, err) = p.communicate()  
                                    p_status = p.wait()
                                    with open(failed_file, 'a') as f:
                                        f.write(str(name_original) +','+ str(name) + '\n')
        total_count += 1
