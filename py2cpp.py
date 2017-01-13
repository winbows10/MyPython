import re
import ast

class Py2Cpp:
	def __init__(self, node):
		self.indentLv = 0
		self.node = node
		
		# run print(dir(ast)), and you will see class names below.
		types = ["Name", "Num", "Assign", "Str", "Expr", "Break", 
			"Lt", "Gt", "LtE", "GtE", "Add", "BinOp", "And",
			"Or", "Mod", "Return", "Eq", "Continue", "Mult", "Sub",
			"BitOr", "BitAnd", "AugAssign", "FunctionDef", "Compare",
			"NameConstant", "Attribute", "Div", "FloorDiv", "NotEq",
			"Call", "Index", "Subscript", "If", "While", "Delete"]
			# ToDo: Slice, List, ClassDef, For, Dict, Bytes, ListComp, comprehension, Lambda...
		
		self.astMethods = {} # The types of keys are ast class types.
		for i in types:
			self.astMethods[getattr(ast, i)] = getattr(self, "get{}Code".format(i))
		
		self.forwardDeclarations = {} # {symbol: code}
		self.prototypes = {} 
	
	def getIndentStr(self):
		ret = ""
		for i in range(0, self.indentLv):
			ret += "\t"
		return ret
	
	def getCode(self, n):
		return self.astMethods[type(n)](n)
	
	def getFunctions(self):pass
	def getClasses(self):pass
	
	#################################################################
	##
	## The methods' names are very important.
	## Each must be defined in a format, "get[ast type]Code"
	##
	
	def getDeleteCode(self, n):
		ret = ""
		for i in n.targets:
			ret += self.getIndentStr() + "delete " + self.getCode(i) + ";\n"
			if True:
				ret += self.getIndentStr()
				ret += self.getCode(i) + " = NULL;\n"
		return ret
	
	def getWhileCode(self, n):
		ret = self.getIndentStr() + "while("
		ret += self.getCode(n.test) + "){\n"
		
		#body
		self.indentLv += 1
		for i in n.body:
			ret += self.getCode(i)
		self.indentLv -= 1
		ret += self.getIndentStr() + "}\n"
		
		if n.orelse:
			raise Exception("AxtuAxutauhruhiagr!!!!")
		
		return ret
	
	def getIfCode(self, n):
		# test
		ret = self.getIndentStr() + "if("
		ret += self.getCode(n.test) + "){\n"
		
		#body
		self.indentLv += 1
		for i in n.body:
			#ret += self.getIndentStr()
			ret += self.getCode(i)
		self.indentLv -= 1
		ret += self.getIndentStr() + "}\n"
		
		#orelse??????????????????????????????????????
		if n.orelse:
			if type(n.orelse[0]) != ast.If:
				ret += "else{\n"
				self.indentLv += 1
				
				for i in n.orelse:
					#ret += self.getIndentStr() 
					ret += self.getCode(i)
				
				self.indentLv -= 1
				ret += "}\n"
			else:
				ret += "el" + self.getCode(n.orelse[0])
		return ret
	
	def getFunctionDefCode(self, n):
		retType = self.getCode(n.returns)
		funcName = n.name
		
		# arg
		tmpArgs = n.args.args
		tmpStr = retType + " " + funcName + "("
		for i in tmpArgs:
			tmpStr += self.getCode(i.annotation) + " "
			tmpStr += i.arg + ", "
		if tmpArgs:
			tmpStr = tmpStr[:-2]
		tmpStr += "){\n"
		
		# body
		self.indentLv += 1
		bodyStr = ""
		for i in n.body:
			bodyStr += self.getCode(i)
		
		self.indentLv -= 1
		tmpStr += bodyStr + self.getIndentStr() + "}"
		
		return tmpStr
	
	def getSubscriptCode(self, n):
		tmp = self.getCode(n.value)
		tmp += "[" + self.getCode(n.slice) + "]"
		return tmp
	
	def getIndexCode(self, n):
		return self.getCode(n.value)
	
	def getCallCode(self, n):
		tmp = self.getCode(n.func)
		tmp += "("
		for i in n.args:
			tmp += self.getCode(i)
			tmp += ", "
		if n.args:
			tmp = tmp[:-2]
		tmp += ")"
		return tmp
	
	def getDivCode(self, n):
		return " / "
	
	def getFloorDivCode(self, n):
		return " / "
	
	def getAttributeCode(self, n):
		tmp = self.getCode(n.value)
		return tmp + "->" + n.attr
	
	def getCompareCode(self, n):
		if len(n.ops) > 1:
			raise Exception("HAHAHAHAHAHAHAHAHA")
		tmpStr  = self.getCode(n.left)
		tmpStr += self.getCode(n.ops[0]) 
		tmpStr += self.getCode(n.comparators[0])
		
		return "(" + tmpStr + ")"
	
	def getBitAndCode(self, n):
		return " & "
	
	def getBitOrCode(self, n):
		return " | "
	
	def getContinueCode(self, n):
		return "continue;\n"
	
	def getNameCode(self, n):
		return n.id
	
	def getStrCode(self, n):
		return n.s
	
	def getNumCode(self, n):
		return str(n.n)
	
	def getBreakCode(self, n):
		return "break"
	
	def getAugAssignCode(self, n):
		
		target = self.getCode(n.target)
		op = re.search("\S+", self.getCode(n.op)).group()
		value  = self.getCode(n.value)
		return self.getIndentStr() + target + " " + op + "= " + value + ";\n"
	
	def getAssignCode(self, n):
		if len(n.targets) > 1:
			raise Exception("GWAAAAAAAAA!!!!!")
		target = self.getCode(n.targets[0])
		value  = self.getCode(n.value)
		
		# process declarations
		if type(n.value) == ast.Call and type(n.value.func) == ast.Name and n.value.func.id == "decl":
			typeName = self.getCode(n.value.args[0])
			if len(n.value.args) == 1:
				return self.getIndentStr() + typeName + " " + target + ";\n"
			else:
				tmp  = self.getIndentStr() + typeName + " " + target + " = " 
				tmp += self.getCode(n.value.args[1]) + ";\n"
				return tmp
		else:
			# Most of calls are processed below
			return self.getIndentStr() + target + " = " + value + ";\n"
	
	def getBinOpCode(self, n):
		left = self.getCode(n.left)
		op = self.getCode(n.op)
		right = self.getCode(n.right)
		return "(" + left + op + right + ")"
	
	def getReturnCode(self, n):
		value = ""
		if n.value:
			value = self.getCode(n.value)
		return self.getIndentStr() + "return " + value + ";\n"
	
	def getAndCode(self, n):
		return " && "
	
	def getOrCode(self, n):
		return " || "
	
	def getLtCode(self, n):
		return " < "
	
	def getLtECode(self, n):
		return " <= "
	
	def getGtCode(self, n):
		return " > "
	
	def getGtECode(self, n):
		return " >= "
	
	def getEqCode(self, n):
		return " == "
	
	def getNotEqCode(self, n):
		return " != "
	
	
	def getModCode(self, n):
		return " % "
	
	def getAddCode(self, n):
		return " + "
	
	def getMultCode(self, n):
		return " * "
	
	def getSubCode(self, n):
		return " - "
	
	def getExprCode(self, n):
		return self.getIndentStr() + self.getCode(n.value) + ";\n"
	
	def getNameConstantCode(self, n):
		tmp = str(n.value)
		ret = {"True": "true", "False": "false", "None": "NULL"}
		return ret[tmp]
	
	


if __name__ == '__main__':
	# test the class
	node = ast.parse("del a, h").body[0]
	obj = Py2Cpp(node)
	print(obj.getCode(node))
