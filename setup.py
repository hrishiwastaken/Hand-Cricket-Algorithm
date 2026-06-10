import subprocess
import sys
print("Installing necessary modules...")
modules = ["numpy", "pandas"]  # List of modules to install
for module in modules:
    subprocess.check_call([sys.executable, "-m", "pip", "install", module])
print("Module Setup Finished.")
exit()
