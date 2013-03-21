import epydoc
import pickle
import sys
import os
import tempfile
import subprocess
import vt_templates
import inspect
import numpy
try:
    import cdms2
    hasCDMS2 = True
except:
    hasCDMS2 = False

if not os.uname()[0] == "Darwin":
    pth = sys.prefix+"/vistrails/vistrails"
else:
    pth = "/".join(sys.prefix.split("/")[:-5])+"/vistrails/vistrails"

sys.path.append(pth)

import core.application as vt_app

## Function needed to unpickle epydoc's results
def pickle_persistent_load(identifier):
    """Helper for pickling, which allows us to save and restore UNKNOWN,
    which is required to be identical to apidoc.UNKNOWN."""
    if identifier == 'UNKNOWN': return epydoc.apidoc.UNKNOWN
    else: raise pickle.UnpicklingError, 'Invalid persistent id'


def py2Module(value,Type):
    try:
        Type = eval(Type)
        import numpy
        import core.modules
        '''So far only supports int, float, list and module for anything else'''
        if Type in (int, numpy.int,numpy.int0,numpy.int16,numpy.int32,numpy.int64,numpy.int8):
            t = 'core.modules.basic_modules.Integer'
        elif Type in (float,numpy.float,numpy.float128,numpy.float32,numpy.float64):
            t = 'core.modules.basic_modules.Float'
        elif Type==list:
            t = 'core.modules.basic_modules.List'
        elif Type in [str,unicode]:
            t = 'core.modules.basic_modules.String'
        elif Type==dict:
            t = 'core.modules.basic_modules.Dictionary'
        elif Type==file:
            t = 'core.modules.basic_modules.File'
        elif hasCDMS2 and Type == cdms2.tvariable.TransientVariable:
            t = "packages.uvcdat_cdms.init.CDMSVariable"
        else:
            t = str(t) #core.modules.basic_modules.Module
        return t
    except Exception,err:
        print err
        return Type



## processing function
def process_module(m,identifier):
    classes_str = ""
    init_str = ""
    ## first picks the module level infos
    M={} # will contain list of input names and acceptable types
    for k in m.variables.keys():
        v=m.variables[k]
        cname = "_".join(v.canonical_name)
        M[cname] = {}
        val = v.value
        if hasattr(val,"variables"):
            specs={}
            if not val.variables.has_key("__init__"):
                print "skipping class",v.name
                continue
            class_str = vt_templates.defcontainerclass % (
                v.name,
                )
            init = val.variables['__init__'].value
            C, I, S, D = processInputs(init,init.all_args()[1:],"self.container",v.name+"Container")
            class_str+=C
            init_str+=I
            init_str+="    reg.add_output_port(%sContainer, 'container',(%sContainer,'generic container output port'))\n" % (v.name,v.name)

            specs=S
        elif not hasattr(val,"all_args"):
            print "skipping module variable"#,dir(val)
            continue
        else:
            menu = v.canonical_name[0]
            for g in m.group_specs:
                if v.name in g[1]:
                    menu = g[0]
                    if menu[0]=='.':
                        menu = v.canonical_name[0] + menu
                    break
            class_str = vt_templates.defclass % (cname,)
            inputs = val.all_args()
            ret_str = ""
            C, I, S, D = processInputs(val,inputs,"R",cname)
            class_str+=C
            init_str+=I
            specs=S
            specs['UVCDAT_menu']=menu
            ## Ok now we deal with the return value
            outtypes = val.return_type.to_plaintext("").strip()
            p = prep_type(outtypes)
            if isinstance(p,list):
                class_str+="""
        R=self.flat(R)
        for i,r in enumerate(R):\n"""
                for t in p:
                    class_str+=getResultString(t,inc=4,inloop="[i]")
            else:
                class_str+="%s" % getResultString(p,inloop=False)
            #class_str+=prop_str
            init_str += prep_return(cname,outtypes)[1]
        classes_str+=class_str%repr(specs)
    return M,classes_str,init_str

def getResultString(t,inc=0,inloop=True):
    inc+=8
    incst = "%%%is" % inc
    incst = incst % " "
    if inloop:
        outnb = "'out%%i' %%i"
    else:
        index=""
        outnb = "'out0'"
    if t=="cdms2.tvariable.TransientVariable":
        if inloop:
            st = "%stmp = r""\n" % (incst)
        else:
            st = "%stmp = R""\n" % (incst)
        st+= "%snr = packages.uvcdat_cdms.init.CDMSVariable(filename=None,name=tmp.id)\n" %(incst)
        st+= "%snr.var=tmp\n" % incst
        st+= "%sself.setResult(%s,nr)\n" % (incst,outnb)
    else:
        if inloop:
            st = "%sself.setResult(%s,r)\n" % (incst,outnb)
        else:
            st = "%sself.setResult(%s,R)\n" % (incst,outnb)
    return st


def processInputs(val,inputs,oname,cname):
    init_str = ""
    specs = {}
    class_str = ""
    init_str+="""\n    reg.add_module(%s)\n""" % (cname)
    for a in inputs:
        types = prep_type(val.arg_types[a].to_plaintext("").strip())
        #prop_str +=  vt_templates.prop % (a,a,a,a,types,a,types)
        descr="generic description for param: %s" % a
        for d in val.arg_descrs:
            if d[0]==a:
                descr = d[1].to_plaintext("").strip()
                break
        mtype = py2Module(None,types)
        if mtype[0]=="'":
            init_str += """    reg.add_input_port(%s, '%s',
        (%s))\n""" % (cname,a,mtype)
        else:
            init_str += """    reg.add_input_port(%s, '%s',
        (%s,'%s'))\n""" % (cname,a,mtype,descr)
        class_str+="""        %s = self.getInputFromPort('%s')
        if isinstance(%s,UReADContainer):
          %s=%s.container
        if isinstance(%s,packages.uvcdat_cdms.init.CDMSVariable):
          %s=%s.var\n""" % (a,a,a,a,a,a,a,a,)
    if oname=="self.container":
        Cname = ".".join(val.canonical_name[:-1])
    else:
        Cname = ".".join(val.canonical_name)
    class_str += "        %s = %s(%s)\n" % (oname,
                                     Cname,
                                     ", ".join(inputs)
                                     )
    if val.extra_docstring_fields!=epydoc.apidoc.UNKNOWN: #Special fields
        for e in val.extra_docstring_fields:
            specs[e.tags[0].strip()]=e.plural.strip()
    return class_str,init_str,specs,types

def prep_type(type,inc="",debug=False):
    if debug: print inc,"got:",type
    ipa = type.find("(")
    isq = type.find("[")
    if ipa==-1:
        i1=isq
    elif isq!=-1:
        i1 = min(ipa,isq)
    else:
        i1=ipa
        
    ic = type.find(",")
    out = []
    first = type[i1]
    if first == "[":
        last = "]"
    else:
        last=")"
    if i1==-1:
        if ic==-1:
            if debug: print inc,"path1"
            return str(type).strip()
        else:
            if debug: print inc,"path2"
            for t in type.split(","):
                out.append(prep_type(t,inc+"\t"))
    elif i1==0 and type[-1]==last:
        if debug: print inc,"sending in:",type[1:-1]
        return prep_type(type[1:-1],inc="\t")
    else: #ok now it is getting complicated...
        if debug: print inc,"path3"
        if type[0]==first:
            type=type[1:]
        ic = type.find(",")
        while -1<ic<i1:
            out.append(prep_type(type[:ic],inc+"\t"))
            type=type[ic+1:]
            ic = type.find(",")
            ipa = type.find("(")
            isq = type.find("[")
            if ipa==-1:
                i1=isq
            elif isq!=-1:
                i1 = min(ipa,isq)
            else:
                i1=ipa
        i2 = type.rfind(last)
        if i2!=len(type)-1:
            if debug: print inc,"not full!",first,last,i2,len(type),type
            out.append(prep_type(type[:i2+1],inc+"\t"))
            type=type[i2+1:]
            ic = type.find(",")
            type=type[ic+1:]
            sp=type.split(",")
            for s in sp:
                out.append(prep_type(s,inc+"\t"))
        else:
            out.append(prep_type(type[:i2],inc+"\t"))

            
    return out
                
def prep_return(name, ret,count=0):
    out=""
    ret=ret.strip()
    if not ret[0] in ["[","("]:
        out="    reg.add_output_port(%s, 'out0',(%s,'generic %s output port'))\n" % (name,py2Module(None,ret),ret)
    else:
        for i,t in enumerate(prep_type(ret)):
            out+="    reg.add_output_port(%s, 'out%i',(%s,'generic %s output port'))\n" % (name,i,py2Module(None,t),t)
    return count,out


if __name__=="__main__":
    wrapped = sys.argv[1]
    ## Following needs to be picked up from doc strings
    package_name = 'samplepkg'
    identifier = 'gov.llnl.uread.%s' % package_name
    version = '1.0'
    pth = os.path.abspath(os.path.dirname(wrapped))
    sys.path.insert(0,pth)
    wrapped = os.path.basename(wrapped)
    if wrapped[-3:].lower()==".py":
        wrapped=wrapped[:-3]
    cmd = " ".join([sys.prefix+"/bin/epydoc --pickle -o temp",] + sys.argv[1:])
    p = subprocess.Popen(cmd,shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    p.wait()
    f=open("temp.pickle",'rb')
    u = pickle.Unpickler(f)
    u.persistent_load = pickle_persistent_load
    epy = u.load()
    fo = open(os.path.join(os.environ["HOME"],".vistrails","userpackages","%s.py" % package_name),"w")
    intro = vt_templates.intro % (version,package_name,identifier,pth,wrapped)#,"".join(inspect.getsourcelines(py2Module)[0]))
    print >> fo, intro
    init = vt_templates.init
    for m in epy.root:
        M,C,I = process_module(m,identifier)
        print M
        print >> fo, C
        init+=I
    print >> fo,init
    fo.close()
    print "done"
