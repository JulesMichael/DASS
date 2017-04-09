import re
import ast
import urllib.parse

class block(object):
    """
        Ignore that
    """
    def __init__(self,**kwargs):
        self.__dict__.update(kwargs)

class Parser():
    def __init__(self,text):
        # Vars
        self.text = text
        self.__str__ = ""
        # Processing
        self.__creatIndentation()
        self.__creatBlocks()
        self.__toClass()
        self.__toStr()
    
    def __creatIndentation(self):
        """
        First part of parsing. Find indentation for all lines.
        """
        datas = dict()
        self.indentationList = []
        self.lines = []
        for line in self.text.split("\n"):
            if len(line) > 0:
                if line[0] == " ":
                    newLine = line.lstrip(" ")
                    lineIndentation = len(line) - len(line.lstrip(" "))
                elif line[0] == "\t":
                    newLine = line.lstrip("\t")
                    lineIndentation = len(line) - len(line.lstrip("\t"))
                else:
                    newLine = line
                    lineIndentation = 0

                self.lines.append(newLine.strip())
                self.indentationList.append(lineIndentation)
    

    def __creatBlocks(self):
        """
        Second part of parsing. Find blocks and creat a list.
        """
        w = list(zip(self.lines,self.indentationList))
        self.blocks, indentation, level = "[", 0 , 0
        for i in w:
            if i[1] > indentation :
                level = level + 1
                self.blocks += ",[" + '"' + urllib.parse.quote_plus(i[0]) + '"'
            elif i[1] == 0:
                if len(self.blocks) > 1 : self.blocks += "]"* (level) + ','
                self.blocks += '"' + urllib.parse.quote_plus(i[0]) + '"'
                level = 0
            elif i[1] < indentation :
                self.blocks += "]"* (level) + "," + '"' + urllib.parse.quote_plus(i[0]) + '"'
                level += -1
            elif i[1] == indentation :
                self.blocks += "," + '"' + urllib.parse.quote_plus(i[0]) + '"'
            indentation = i[1]
        self.blocks += "]"* (level+1)
        self.blocks = ast.literal_eval(self.blocks)

    def __toClass(self):
        """
        Fird part of parsing. Transform text into class.
        """
        def parse (subject):
            for i in range(len(subject)):
                if type(subject[i]) == str:
                    theStr = urllib.parse.unquote_plus(subject[i])
                    commentaireRegex = re.match(r"//( )?(.*)", theStr)
                    conditionIfRegex = re.match(r"if (.*):",theStr)
                    conditionElseRegex = re.match(r"else()?:",theStr)
                    conditionElifRegex = re.match(r"elif (.*):",theStr)
                    varriableRegex = re.match(r"§([A-Za-z0-9_-]*)( )?=( )?(.*)( )?;",theStr)
                    functionRegex = re.match(r"function (.*)( )?\((.*)\)()?:",theStr)
                    regleRegex = re.match(r"^(.*)( )?:( )?(.*);",theStr)
                    selectorRegex = re.match(r"^(.*)( )?:$",theStr)
                    if commentaireRegex :
                        subject[i] = block(type="commentaire",value=commentaireRegex.group(2))
                    elif conditionIfRegex :
                        subject[i] = block(type="conditionIf",condition=conditionIfRegex.group(1),content=parse(subject[i+1]))
                        subject[i+1] = None
                    elif conditionElseRegex :
                        subject[i] = block(type="conditionElse",content=parse(subject[i+1]))
                        subject[i+1] = None
                    elif conditionElifRegex :
                        subject[i] = block(type="conditionElif",condition=conditionElifRegex.group(1),content=parse(subject[i+1]))
                        subject[i+1] = None
                    elif varriableRegex:
                        subject[i] = block(type="variable",name=varriableRegex.group(1),value=varriableRegex.group(4))
                    elif functionRegex:
                        subject[i] = block(type="function",name=functionRegex.group(1) or None,args = functionRegex.group(3).split(","),content=parse(subject[i+1]))
                        subject[i+1] = None
                    elif regleRegex:
                        subject[i] = block(type="regle",property=regleRegex.group(1),value=regleRegex.group(4))
                        subject[i+1] = None
                    elif selectorRegex:
                        subject[i] = block(type="selector",selector=selectorRegex.group(1),content=parse(subject[i+1]))
                        subject[i+1] = None
                    else:
                        subject[i] = block(type="unknown")
                elif type(subject[i]) == list:
                    subject[i] = parse(subject[i])
            while None in subject:
                subject.remove(None)
            return subject
        self.blocks = parse(self.blocks)

# Usage
p = Parser(open("test.dass","r").read())
#print(p.blocks)
print(p.__str__)


"""
Whene you are codding use:
./autorun.py watch "__main__.py;test.dass" exec "python3 __main__.py"

Whene you are testing use:
python3 __init__.py
"""


"""
def pr (l,level = 0):
    for i in l:
        if type(i) == str:
            l = re.sub(r'§(?P<var_name>[A-Za-z0-9_-]*)( )?=( )?(?P<var_value>.*)( )?;',"var \g<var_name> = \g<var_value>;",urllib.parse.unquote_plus(i)) # Déclaration de varriables
            self.__str__ += "\t"*level + l + '\n' 
        elif type(i) == list :
            pr(i,level +1 )
pr(self.blocks)
"""