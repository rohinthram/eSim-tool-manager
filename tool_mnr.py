import os
import sys
import shutil
import requests
from tqdm.auto import tqdm
import subprocess

from py7zr import pack_7zarchive, unpack_7zarchive
shutil.register_archive_format('7zip', pack_7zarchive, description='7zip archive')
shutil.register_unpack_format('7zip', ['.7z'], unpack_7zarchive)

#print(sys.argv)

cfg = open(f'C:/Users/{os.getlogin()}/.esim/config.ini').read().split('\n')
eSim_HOME = cfg[1][cfg[1].find('= ')+2:]
home_1 = '/'.join(eSim_HOME.split('\\')[:-1]).strip()
def install(pkg):
    if pkg == 'makerchip':
        try:
            url = "https://github.com/FOSSEE/eSim/raw/installers/Windows/makerchip.7z"

            out_file = "makerchip.7z"

            with requests.get(url, stream=True) as r:
                # check header to get content length, in bytes
                total_length = int(r.headers.get("Content-Length"))
                
                # implement progress bar via tqdm
                with tqdm.wrapattr(r.raw, "read", total=total_length, desc="")as raw:
                
                    # save the output to a file
                    with open(out_file, 'wb')as output:
                        shutil.copyfileobj(raw, output)

            print('[INFO] Received the payload')

            #extract the received zip file
            path_to_extract = '.'.join(out_file.split('.')[:-1])
            shutil.unpack_archive(out_file, path_to_extract)
            
            destination = f'{home_1}/MSYS/mingw64/bin/'
            
            os.chmod(destination, 777)
            shutil.copy(f'{path_to_extract}/{path_to_extract}/makerchip.exe', destination)
            shutil.copy(f'{path_to_extract}/{path_to_extract}/sandpiper-saas.exe', destination)

            shutil.rmtree(path_to_extract)
            os.remove(out_file)
            
            print('[INFO] Package Installed!')
            return 1

        except Exception as e:
            print(f'[ERROR] {e}')
            return 0
        

    if pkg == "sky130":
        try:
            url = "https://github.com/google/skywater-pdk-libs-sky130_fd_pr"
            current_loc = os.getcwd()
            os.chdir(f'{eSim_HOME}/library')
            prc =  subprocess.Popen(f"git clone {url}", shell=True, stdout=subprocess.PIPE).stdout
            log =  prc.read().decode('utf-8')
            print(f'[INFO] {log}')
            if 'Error' in log:
                raise Exception('Unknown Error')
            os.mkdir('sky130_fd_pr')
            os.system("mv skywater-pdk-libs-sky130_fd_pr/* sky130_fd_pr/")
            subprocess.call(['chmod', '-R', '+w', 'skywater-pdk-libs-sky130_fd_pr'])
            shutil.rmtree('skywater-pdk-libs-sky130_fd_pr')

            print('[INFO] Package Installed!')
            os.chdir(current_loc)
            return 1
        except Exception as e:
            print(f'[ERROR] {e}')
            return 0

def uninstall(pkg):
    if pkg == 'makerchip':
        try:
            path = f'{home_1}/MSYS/mingw64/bin/'
            os.chmod(path, 777)
            os.remove(f'{path}/makerchip.exe')
            os.remove(f'{path}/sandpiper-saas.exe')
            
            return 1
        except Exception as e:
            print(f'[ERROR] {e}')
            return 0
    elif pkg == 'sky130':
        try:
            shutil.rmtree(f'{eSim_HOME}/library/sky130_fd_pr')
            return 1
        except Exception as e:
            return 0

if len(sys.argv) != 3:
    print("Invalid process request")
    exit(0)

if sys.argv[2] not in ['makerchip', 'sky130']:
    print("Invalid process request")
    exit(0)

if sys.argv[1] == 'install':
    install(sys.argv[2])
elif sys.argv[1] == 'uninstall':
    uninstall(sys.argv[2])
else:
    print("Invalid process request")
    exit(0)
