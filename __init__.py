import re
import ast
import urllib.parse

class block(object):
    def __init__(self,header=None,content=[],container = None):
        self.header = header
        self.content = content
        self.container = container

class Parser():
    def __init__(self,text):
        self.text = text
        self.__creatIndentation()
        self.__creatBlocks()
        self.__str__ = ""
        self.__parse()
    
    def __creatIndentation(self):
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

                self.lines.append(newLine)
                self.indentationList.append(lineIndentation)
    

    def __creatBlocks(self):
        w = list(zip(self.lines,self.indentationList))
        self.blocks, indentation, level = "[", 0 , 0
        for i in w:
            if i[1] > indentation :
                level = level + 1
                self.blocks += ",[" + '"' + urllib.parse.quote_plus(i[0]) + '"'
            elif i[1] == 0:
                if len(self.blocks) > 1 : 
                    self.blocks += "]"* (level);
                    self.blocks += ','
                    
                self.blocks += '"' + urllib.parse.quote_plus(i[0]) + '"'
                level = 0
            elif i[1] < indentation :
                self.blocks += "]"* (level) + "," + '"' + urllib.parse.quote_plus(i[0]) + '"'
                level += -1
            elif i[1] == indentation :
                self.blocks += "," + '"' + urllib.parse.quote_plus(i[0]) + '"'
                level += 0
            indentation = i[1]
        self.blocks += "]"* (level+1)
        self.blocks = ast.literal_eval(self.blocks)

    def __parse(self):
        def pr (l,level = 0):
            for i in l:
                if type(i) == str:
                    l = re.sub(r'§(?P<var_name>[A-Za-z0-9_-]*)( )?=( )?(?P<var_value>.*)( )?;',"var \g<var_name> = \g<var_value>;",urllib.parse.unquote_plus(i))
                    self.__str__ += "\t"*level + l + '\n' # Déclaration de varriables urllib.parse.unquote_plus(i)
                elif type(i) == list :
                    pr(i,level +1 )
        pr(self.blocks)


def pr (l,level = 0):
    for i in l:
        if type(i) == str:
            print("\t"*level, urllib.parse.unquote_plus(i))
        elif type(i) == list :
            pr(i,level +1 )

p = Parser(open("test.dass","r").read())
print(p.__str__)

"""
./autorun.py watch "__init__.py;test.dass" exec "python3 __init__.py
"""