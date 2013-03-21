# samples of function/method declarations to be parsed into VisTrails objects.
# This is epydoc style, but we will have to add  more requirements, e.g. structure parameter and
# return value descriptions.
"""
@requires: cdms2
@author: Charles Doutriaux
@author: Jeff Painter
@author: Kate Marvel
@organization: LLNL
@license: Free BSD
@contact: doutriaux1@llnl.gov
@summary: Sample U-ReAD file
@version: 0.0.4
@warning: Not intended for any real usage
@bug: Probably many
@bug: Probably even more !
## Use group to put functions into menus.submenus
## top menu will be module name if no name is specified before first "."
@group .Sub1: sss_neighbors foo1
@group .Sub1.Sub2: foo2 foo3
@group Second: foo4
@sort: foo4 foo3 foo2 foo1 sss_neighbors
"""
import cdms2
class SphericalScaleSpace():
    def __init__(self,var,fname):#,num_stages = 3,num_octaves = 5,tree = None, fig=None):
        """The constructor.
        @param var: Input variable
        @type var: str
        @param fname: Input file
        @type fname: str
        """
        self.data = cdms2.open(fname)(var,longitude=(-180,180))
        # rest of the actual method is omitted
    def neighbors(self,point=[0,0]):
        """ get nearest neighbors"""
        Z = self.spherical_gaussian(point,.2)
        return Z.flatten().argsort()[-9::]
    
def sss_neighbors(S,T):
    """get nearest neighbors.
    @param S: describes the space in which neighbors are to be found
    @type S: SphericalScaleSpaceContainer
    @param T: Temperature
    @type T: float
    @rtype: (float, float) 
    @return: pairs each defining a neighbor point
    @newfield uread: True
   """
    return (0,1)

def max(S):
    """get nearest neighbors.
    @param S: describes the space in which neighbors are to be found
    @type S: cdms2.tvariable.TransientVariable
    @rtype: float
    @return: max
    @newfield uread: True
   """
    return S.max()

def twice(S):
    """get nearest neighbors.
    @param S: describes the space in which neighbors are to be found
    @type S: cdms2.tvariable.TransientVariable
    @rtype: cdms2.tvariable.TransientVariable
    @return: max
    @newfield uread: True
   """
    return S*2.

      
def foo1(a,b):
    """
    @param a: First number
    @type a: float
    @param b: Second Number
    @type b: float
    @return: sum of a and b
    @rtype: float
    """
    return a+b

def foo2(a,b):
    """
    @param a: First number
    @type a: float
    @param b: Second Number
    @type b: float
    @return: diff of a and b
    @rtype: float
    """
    return a-b

def foo3(a,b):
    """
    @param a: First number
    @type a: float
    @param b: Second Number
    @type b: float
    @return: div of a and b
    @rtype: float
    """
    return a/b

def foo4(a,b):
    """
    @param a: First number
    @type a: float
    @param b: Second Number
    @type b: float
    @return: product of a and b
    @rtype: float
    """
    return a*b
