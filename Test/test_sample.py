
# CDMSVariable args?
# axes (String): level=(1000.0, 10.0),longitude=(0.0, 357.5),time=('1987-6-1 0:0:0.0', '1988-4-1 0:0:0.0'),latitude=(-90.0, 90.0),squeeze=1,
# axesOperations String: {'latitude': 'def', 'level': 'def', 'longitude': 'def', 'time': 'def'}
# file File: /lgm/uvcdat/master/Library/Frameworks/Python.framework/Versions/2.7/sample_data/ta_ncep_87-6-88-4.nc
#name String: ta
#varNameInFile String: ta

import os
import sys

if not os.path.exists(os.path.join(os.environ["HOME"],".vistrails","userpackages")):
    raise "Error please run vistrails once first"

if not os.uname()[0] == "Darwin":
    pth = sys.prefix+"/vistrails/vistrails"
else:
    pth = "/".join(sys.prefix.split("/")[:-5])+"/vistrails/vistrails"


sys.path.append(pth)

pkgnm = "samplepkg"

import core.application as vt_app
from core.packagemanager import get_package_manager
import core.modules.vistrails_module

print "imported vt"
print 'Initing'
vt_app.init({'dotVistrails': '.vistrails','output':''})
#vt_app.init({'output':''})
print "Voila"
pm = get_package_manager()
print "Voila"

import core.api
print "imported core"
vt=core.api.get_api()


basic = vt.get_package("edu.utah.sci.vistrails.basic")

for p,c in [
    ("edu.utah.sci.vistrails.spreadsheet","spreadsheet"),
    ("gov.llnl.uvcdat","uvcdat"),
    ("gov.llnl.uvcdat.cdms","uvcdat_cdms"),
    ## ("edu.utah.sci.vistrails.vtk","vtk"),
    ## ("edu.utah.sci.vistrails.numpyscipy","NumSciPy"),
    ("gov.llnl.uread.%s" % pkgnm,pkgnm),
    #("",""),
    ]:
    try:
        print "getting on",p,c
        pkg = vt.get_package(p)
    except:
        print "late enable"
        pm.late_enable_package(c)

pth = os.path.abspath(os.path.dirname(os.getcwd()))
sys.path.insert(0,pth)

print "OK all init now what are the packages we have?"
print "Getting package"

pkg = pm.enabled_package_list()
for p in pkg:
    print '\t',p.codepath

print "loading in"
import sample

uvcdms = vt.get_package('gov.llnl.uvcdat.cdms')
print uvcdms

#V = uvcdms.CDMSVariable(axes = "level=(1000.0, 10.0),longitude=(0.0, 357.5),time=('1987-6-1 0:0:0.0', '1988-4-1 0:0:0.0'),latitude=(-90.0, 90.0),squeeze=1",
#                        axesOperations="{'latitude': 'def', 'level': 'def', 'longitude': 'def', 'time': 'def'}",
#                        file = "/lgm/uvcdat/master/Library/Frameworks/Python.framework/Versions/2.7/sample_data/ta_ncep_87-6-88-4.nc",
#                        name = 'ta',
#                        varNameInFile = "ta",
#                        )
fnm = sys.prefix+'/sample_data/clt.nc'
V = uvcdms.CDMSVariable(file=fnm,
                        name='clt',
                        )
smpl = vt.get_package('gov.llnl.uread.%s' % pkgnm)

SS = smpl.SphericalScaleSpaceContainer()
SS.var = 'clt'
SS.fname = sys.prefix+"/sample_data/clt.nc"

ST = smpl.sample_twice()

ST.S = V

SN = smpl.sample_max()
SN.S=ST.out0



vt.tag_version("bla")

ret = vt.execute()


print "done"
op = ret[0][0].objects[SN._module.id].outputPorts
print op['out0']

vt.save_vistrail("sample.vt")
