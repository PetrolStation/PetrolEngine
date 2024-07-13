import re
import sys

# returns min of values except -1 (will return -1 if both are -1)
def emin(a: int, b: int) -> int:
    if a == -1: return b
    if b == -1: return a

    if a <= b: return a
    if b <= a: return b
    
# get list of scope names and their range of code
def getScopes(content: str) -> list:
    scopes = [
        ["", 0, 0]
    ]

    def firstUnclosed():
        for x in reversed(scopes):
            if x[2] == -1: return scopes.index(x)
        return None

    cursor = 0
    while True:
        pos = emin(
            content.find('{', cursor),
            content.find('}', cursor)
        )

        if pos == -1: break

        if(content[pos] == '{'):
            lpos =  max(cursor, content.rfind('\n', 0, pos))
            rpos = emin(content.rfind(':', lpos, pos), content.rfind('(', lpos, pos))
            rpos = emin(rpos, pos)
            name = content[lpos:rpos]
            name = re.sub("noexcept|const", '', name).strip().split(' ')[-1].strip()
            scopes.append([name, pos, -1])
        if(content[pos] == '}'):
            scopes[firstUnclosed()][2] = pos
        cursor = pos+1
    scopes[0][2] = len(content)
    return scopes


# returns path to the scope like "::myNamespace::myClass::"
def getScopePath(pos: int, scopes: list) -> str:
    path = ""
    for scope in scopes:
        if pos < scope[2] and pos > scope[1]:
            path += scope[0] + "::"
    return path

# get name of the attribiute subject ex. for "[[foo]] int size;" will return "size"
def getAttributeSubject(pos: int, content: str) -> str:
    rpos = emin(
        emin(
            content.find(";", pos),
            content.find("=", pos),
        ),
        emin(
            content.find("(", pos),
            content.find("{", pos),
        )
    )

    subject = content[pos:rpos].strip().split(' ')[-1].strip()
    
    return subject

# TODO: error detection for no arguments specified
def genArguments(attrs: dict, usages: dict, name: str) -> list:
    args = []
    attr = name
    if True:
        if "def" in attrs[attr]['properties']:
            for usage in usages[attr]:
                for arg in attrs[attr]['call']:
                    if arg in usage: args.append(usage[arg])
                content += "__{}({});".format(attr, args) + EOL
        if "sum" in attrs[attr]['properties']:
            for arg in attrs[attr]['call']:
                literal  = False
                initList = False
                if "'" in arg: literal = True
                if "{" in arg: initList = True
                subjects = ", ".join([literal*'"'+usage[arg]+literal*'"' for usage in usages[attr]])
                args.append(initList*"{" + subjects + initList*"}")

    return args

# makes a file that calls all attributes functions
def genDefs(attrs: dict, usages: dict, includes: list, name: str) -> str:
    EOL = "\r\n"
    content = '#include "{}Attributes.h"'.format(name) + EOL

    for include in includes:
        content += "#include <{}>".format(include) + EOL
    
    content += EOL

    for attr in attrs.keys():
        if "global" not in attrs[attr]['properties']: continue
        if "def" in attrs[attr]['properties']:
            for usage in usages[attr]:
                args = []
                
                for arg in attrs[attr]['call']:
                    argi = re.sub("\(|\)|'", "", arg)
                    if argi in usage:
                        literal = "'" in arg
                        args.append(literal*'"'+usage[argi]+literal*'"')

                content += "__{}({});".format(attr, ", ".join(args)) + EOL
        if "sum" in attrs[attr]['properties']:
            args = []
            
            for arg in attrs[attr]['call']:
                literal  = False
                initList = False
                if "'" in arg: literal = True
                if "{" in arg: initList = True
                subjects = ", ".join([literal*'"'+usage[arg]+literal*'"' for usage in usages[attr]])
                args.append(initList*"{" + subjects + initList*"}")

            content += "__{}({}{}{});".format(
                attr,
                EOL + ' '*4,
                (',' + EOL + ' '*4).join(args),
                EOL + ' '*0
            )
        if "perClass" in attrs[attr]['properties']:
            classes = {}
            for usage in usages[attr]:
                if usage['scope'] not in classes:
                    classes[usage['scope']] = []
                classes[usage['scope']].append(usage)

            for scope in classes:
                classUsages = classes[scope]
                args = []
                for arg in attrs[attr]['call']:
                    literal  = False
                    initList = False
                    if "'" in arg: literal = True
                    if "{" in arg: initList = True
                    argi = re.sub("\(|\)|'", "", arg)
                    if argi in usage and arg in ['scope', 'namespace']:
                        literal = "'" in arg
                        args.append(literal*'"'+usage[argi]+literal*'"')
                    if arg in ['scope', 'namespace']: continue
                    subjects = ", ".join([literal*'"'+usage[arg]+literal*'"' for usage in classes[scope]])
                    args.append(initList*"{" + subjects + initList*"}")
                content += "__{}({}{}{});".format(
                    attr,
                    EOL + ' '*4,
                    (',' + EOL + ' '*4).join(args),
                    EOL + ' '*0
                )

    content += EOL + "bool init{}Attributes()".format(name) + "{" + EOL
    
    content += "    static bool initialized = false;" + EOL
    content += "    if(initialized) return true;" + EOL
    content += "    initialized = true;" + EOL + EOL

    for attr in attrs.keys():
        if "func" not in attrs[attr]['properties']: continue
        if "def" in attrs[attr]['properties']:
            for usage in usages[attr]:
                args = []
                
                for arg in attrs[attr]['call']:
                    argi = re.sub("\(|\)|'", "", arg)
                    if argi in usage:
                        literal = "'" in arg
                        args.append(literal*'"'+usage[argi]+literal*'"')
                
                content += "    __{}({});".format(attr, ", ".join(args)) + EOL
        if "sum" in attrs[attr]['properties']:
            args = []
            
            for arg in attrs[attr]['call']:
                literal  = False
                initList = False
                if "'" in arg: literal = True
                if "{" in arg: initList = True
                subjects = ", ".join([literal*'"'+usage[arg]+literal*'"' for usage in usages[attr]])
                args.append(initList*"{" + subjects + initList*"}")

            content += "    __{}({}{}{});".format(
                attr,
                EOL + ' '*8,
                (',' + EOL + ' '*8).join(args),
                EOL + ' '*4
            )

    content += EOL + "    return true;"
    content += EOL + "}" + EOL

    content += EOL + "bool __{}AttributesInitialized = init{}Attributes();".format(name,name) + EOL

    return content

def genDecs(attrs: dict, name: str) -> str:
    EOL = "\r\n"
    content = "#pragma once" + EOL + EOL

    content += "bool init{}Attributes();".format(name) + EOL

    for attr in attrs.keys():
        if "dec" in attrs[attr]['properties'] and len(attrs[attr]['properties']) == 2:
            content += attrs[attr]['args'][1] + EOL
    return content

def strToArgs(args: str) -> list:
    alpos = args.find('(')
    arpos = args.find(')')
    args = args[alpos+1:arpos].split(",")
    return [x.strip() for x in args]

# returns dict of {'attrName': {type: 'attrType', args: ["arg1", "arg2"]}}
# based on definitions found in content str
def searchAttributeDefs(content: str) -> dict:
    attrs = {}
    cursor = 0
    while True:
        lpos = content.find("MacroAttr", cursor)
        npos = content.rfind("\n", 0, lpos+6)
        dpos = content.rfind("define", npos, lpos+1)
        dpos = max(dpos, content.rfind("//", npos, lpos+1))
        if dpos != -1:
            cursor = lpos+1
            continue
        if lpos == -1: break
        cpos = content.find(")", lpos)
        apos = content.find("(", lpos, cpos)
        properties = []
        call = []
        args = []
        if apos != -1:
            aepos = cpos
            cpos = content.find(")", cpos+1)
            properties = content[apos+1:cpos]
            print(properties)
            properties = properties.split('"')[1:-1][::2]
            for arg in properties:
                if "call" in arg:
                    call = strToArgs(properties.pop(properties.index(arg)))
                if "args" in arg:
                    args = strToArgs(properties.pop(properties.index(arg)))
        rpos = content.find("(", cpos+1)
        name = content[lpos+6:rpos]
        name = re.sub("void|constexpr|#define", '', name).strip().split(' ')[-1].strip()[2:]
        attrs[name] = {'type': "sumMacro", "properties": properties, 'args': args, 'call': call}
        cursor = lpos+6
    cursor = 0
    while True:
        lpos = content.find("[[Attr", cursor)
        npos = content.rfind("\n", 0, lpos+6)
        dpos = content.rfind("define", npos, lpos+1)
        dpos = max(dpos, content.rfind("//", npos, lpos+1))
        if dpos != -1:
            cursor = lpos+1
            continue
        if lpos == -1: break
        cpos = content.find("]]", lpos)
        apos = content.find("(", lpos, cpos)
        properties = []
        call = []
        args = []
        if apos != -1:
            aepos = content.find(")]]", apos, cpos)
            properties = content[apos+1:aepos].split('"')[1:-1][::2]
            for arg in properties:
                if "call" in arg:
                    call = strToArgs(properties.pop(properties.index(arg)))
                if "args" in arg:
                    args = strToArgs(properties.pop(properties.index(arg)))
            #args = content[apos+1:aepos].split(',')
            #for arg in args: attrArgs.append(arg.replace('"', '').strip())
        
        rpos = content.find("(", cpos+1)
        name = content[lpos+6:rpos]
        name = re.sub("void|constexpr|#define", '', name).strip().split(' ')[-1].strip()[2:]
        attrs[name] = {'type': "sumMacro", 'properties': properties, 'args': args, "call": call}
        print(attrs)
        cursor = lpos+6
    return attrs

# returns dict of {'attrName': ["usage1", "usage2"]} found in content str
def searchAttributes(content: str, attrs: list) -> dict:
    scopes = getScopes(content)
    usages = {}
    
    for attr in attrs:
        cursor = 0
        while True:
            pos = content.find("[["+attr+"]]", cursor)
            if pos == -1: break
            path = getScopePath(pos, scopes)
            subject = getAttributeSubject(pos, content)
            if attr not in usages: usages[attr] = []
            usages[attr].append({
                "location":"&"+path+subject,
                "subject": subject,
                "scope": path[:-2],
                "namespace": "::".join(path[2:-2].split("::")[:-1])
            })
            cursor = pos+len(attr)+5
    return usages


# generates output file based on attributes in input files
def parseHeaders(files: list, output: str, name: str):
    includes = []
    
    attrs = {}
    for file in files:
        with open(file) as f:
            fileAttrs = None
            try:
                fileAttrs = searchAttributeDefs(f.read())
            except:
                continue
            if len(fileAttrs.keys()) != 0: includes.append(file)
            
            for key in fileAttrs.keys():
                if key not in attrs: attrs[key] = fileAttrs[key]

    usages = {}
    for file in files:
        with open(file) as f:
            fileUsages = None
            try:
                fileUsages = searchAttributes(f.read(), attrs.keys())
            except:
                continue

            if len(fileUsages.keys()) != 0: includes.append(file)

            for key in fileUsages:
                if key not in usages: usages[key] = []
                usages[key] += fileUsages[key]

    # remove dups
    includes = list(set(includes))
    
    newHeader = True
    newSource = True

    if os.path.isfile(output+ "/" + name +"Attributes.h"):
        with open(output+ "/" + name +"Attributes.h", 'r') as r:
            if(r.read() == genDecs(attrs, name)): newHeader = False

    if os.path.isfile(output+ "/" + name +"Attributes.cpp"):
        with open(output+ "/" + name +"Attributes.cpp", 'r') as r:
            if(r.read() == genDefs(attrs, usages, includes, name)): newSource = False
        
    if(newHeader):
        with open(output+ "/" + name +"Attributes.h", 'w') as w:
            w.write(genDecs(attrs, name))
    if(newSource):
        with open(output+ "/" + name + "Attributes.cpp", 'w') as w:
            w.write(genDefs(attrs, usages, includes, name))
    

if __name__ == "__main__":
    parseHeaders(sys.argv[1:-2], sys.argv[-1], sys.argv[-2])
