import subprocess
import sys

try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'xlwt==1.3.0'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'xlrd==1.2.0'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'xlsxwriter==3.0.2'])
except Exception as e:
    raise