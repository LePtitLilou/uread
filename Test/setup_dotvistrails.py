## Run this once it should generate a dotvistrails

# Initialization routines (specific to user's environment)
import sys
#sys.path.append("/vistrails/src/git/vistrails")
import os
if not os.uname()[0] == "Darwin":
    pth = sys.prefix+"/vistrails/vistrails"
else:
    pth = "/".join(sys.prefix.split("/")[:-5])+"/vistrails/vistrails"

print pth
sys.path.append(pth)
import core.application as vt_app
#vt_app.init({'dotVistrails': '/usr/local/cssef/land_model/clm4_ornl/scripts/UQ/Vistrails/.vistrails'})
vt_app.init({'dotVistrails': '.vistrails','output':''})
