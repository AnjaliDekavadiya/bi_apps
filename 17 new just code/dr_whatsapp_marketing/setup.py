import subprocess
import os
import sys

class Packages:
    get_pckg = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
    installed_packages = [r.decode().split('==')[0] for r in get_pckg.split()]

    required_packages = ['PyYAML', 'heyoo']
    for packg in required_packages:
        if packg in installed_packages:
            pass
        else:
            print('installing package %s' % packg)
            os.system('pip3 install ' + packg)