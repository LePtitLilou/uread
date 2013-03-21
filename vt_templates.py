intro = """
import core.modules.module_registry
import sys
from core.modules.vistrails_module import Module, ModuleError
import packages

version = '%s'
name = '%s'
identifier = '%s'

def package_dependencies():
    return [ 'gov.llnl.uvcdat.cdms' ]

sys.path.insert(0,'%s')
import %s

class UReADContainer(Module):
    pass

"""

init = """
def initialize(*args,**keywords):
    reg = core.modules.module_registry.registry
    reg.add_module(UReADContainer)
"""

defcontainerclass = """
class %sContainer(UReADContainer):
    _uread_specs=%%s
    def compute(self):     
"""


defclass ="""

class %s(Module):
    _uread_specs=%%s
    def flat(self,r,out=[]):
        for p in r:
            if isinstance(p,list):
                flat(p,out)
            else:
                out.append(p)
        return out

    def compute(self):
"""

                
prop = """
    @property
    def %s(self,):
        return self.getInputPort('_%s')
    @%s.setter
    def %s(self,value):
        valid_types="%s".split('|')
        for t in valid_types:
            if isinstance(value,eval(t)):
                self._%s = py2Module(value,eval(t))
                return
        raise RunTimeError, 'Sorry valid types are: %%s ', ''.join(%s) """
