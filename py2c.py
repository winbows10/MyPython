import ast

"""
def func(a: int, b: int)->int:
	tmp = dcl(int, 8)
	
	for i in range(0, tmp):
		tmp += tmp * tmp
	
	return tmp * tmp

# obj = dcl(Test)
# => Test *obj = new Test();

# obj = dcl(Test, 8)
# => Test *obj = new Test(8); #     added *

# obj = dcl(int, 4)
# => int obj = 4;             # not added *

def f(a: pint):pass

"""

VERSION = "0.1.0"


# some C like symbols are later written to another .py file.
# importing this module, pure python mode works well.
Void = None
Int = None
Float = None
Str = None

def dcl(tp, *arg):
	if len(arg): return arg[0]
def cast(tp, sym):pass
def P(tp):pass
def const(tp):pass
def Arr(tp, num, arr = []):pass
def Vec(tp, arr = []):pass
def List(tp, arr = []):pass
def Map(keytype, valtype):pass

# fixed array... arr = Arr(int, 5)
# vector     ... arr = Vec(int)   # vector<int> *arr = new vector<int>();
# vector     ... arr = Vec(int, [1,4,5,3,7]) # const value only?


# for decorators
def override(func):return func    # override
# def fin(func):return func       # destructor

gdic = {"Void": None, "Int": None, "Float": None, "Str": None, "Arr": None, 
	"Vec": None, "List": None, "Map": None, "int": None, "float": None, "str": None}



def _get_node(s):
	return ast.parse(s)


def _get_func_info(m):
	rslt = {}
	rslt["name"] = m.name         # val is str.
	rslt["ret"] = m.returns       # obj.id
	rslt["args"] = m.args.args    # obj[0].arg,  obj[0].annotation.id
	return rslt


def _get_globals(nodes):
	"""
	Now, only functions are available.
	
	ToDo: 
		classes, and get their members and methods, including constructors.
	"""
	gdic = {}
	
	for i in nodes.body:
		if type(i) == ast.FunctionDef:
			tmp = _get_func_info(i)
			gdic[tmp["name"]] = tmp
		elif type(i) == ast.ClassDef:
			_get_classdef_c_code(i, gdic, True)
	
	for i in gdic:
		print("######################################")
		print(i,"SOIYA!",  gdic[i])
	
	return gdic


def _get_funcdef_c_code(f, gdic):
	ret = ""
	func = _get_func_info(f)
	ret += func["ret"].id + " " + func["name"] 
	ret += "("
	
	ldic = {}
	for i in func["args"]:
		ldic[i.arg] = _get_body_c_code(i.annotation, "", gdic, {})
		ret += _get_body_c_code(i.annotation, "", gdic, {}) + " " + i.arg + ", "
	if len(func["args"]):
		ret = ret[:-2]
	ret += "){\n"
	
	print("JTH+JAJGAJHJOORJTOH!!!")
	print(ldic)
	for i in f.body:
		ret += _get_body_c_code(i, "", gdic, ldic)
	
	ret += "}\n"
	return ret


def _get_classdef_c_code(c, gdic, only_layout = False):
	# get __init__ and get member variables.
	# get methods.
	#
	# outputs...
	# A... forward decl
	# B... definition of class layout
	# C... definitions of methods.
	#
	
	info = {}
	info["name"] = c.name
	info["bases"] = [i.id for i in c.bases]
	
	# Get member variables and methods.
	info["vars"] = []
	info["methods"] = []
	for i in c.body:
		if type(i) == ast.FunctionDef and i.name == "__init__":
			for j in i.body:
				# print(j.targets[0].attr)
				if type(j) == ast.Assign and type(j.targets[0]) == ast.Attribute and j.targets[0].value.id == "self":
					info["vars"].append([j.targets[0].attr, _get_body_c_code(j.value.args[0])])
		if type(i) == ast.FunctionDef: # add a method, including __init__()
			info["methods"].append(i)
	
	gdic[c.name] = info
	if only_layout:
		return
	
	ret = []
	ret.append("class " + c.name + ";\n")
	
	defs = ""
	tmp = "class " + c.name
	if len(info["bases"]):
		tmp += ": public "
		for i in info["bases"]:
			tmp += i + ", "
		tmp = tmp[:-2] + "{\npublic:\n"
	for i in info["vars"]:
		tmp += i[1] + " " + i[0] + ";\n"
	for i in info["methods"]:
		rettype = ""
		if i.name != "__init__":
			rettype = _get_body_c_code(i.returns) + " "
			defs += rettype + c.name + "::" + i.name + "("
		else:
			defs += c.name + "::" + c.name + "("
		tmp += rettype + i.name + "("
		if len(i.args.args):
			argcnt = 0
			if i.args.args[0].arg != "self":
				print("STATIC METHOD, NOT IMPLEMENTED YET!!")
			for j in i.args.args:
				if j.arg == "self": 
					continue
				addstr = _get_body_c_code(j.annotation) + " " + j.arg + ", "
				tmp += addstr
				defs += addstr
				
				argcnt += 1
				
			if argcnt:
				tmp = tmp[:-2]
				defs = defs[:-2]
			
		tmp += ");\n"
		defs += "){\n"
		for j in i.body:
			if i.name == "__init__":
				print("##### __init__ SPECIAL!!!")
			defs += _get_body_c_code(j)
		defs += "}\n"
	tmp += "};\n"
	ret.append(tmp)
	print(tmp)
	print(defs)
	tmp = ""
	
	
	return ret


def _get_body_c_code(i, s = "", gdic = {}, ldic = {}):
	func = _get_body_c_code

	if type(i) == ast.Expr:
		s += func(i.value, s, gdic, ldic) + ";\n"

	elif type(i) == ast.Assign:
		if type(i.value) == ast.Call and i.value.func.id == "dcl":
			s += func(i.value.args[0], "", gdic, ldic) + " " + func(i.targets[0], "", gdic, ldic)
			ldic[func(i.targets[0], "", gdic, ldic)] = func(i.value.args[0], "", gdic, ldic)
			
			print("AAAA!!!!!!!!!!!!!\n")
			print(ldic)
			
			if len(i.value.args) > 1:
				s += " = "
				for j in i.value.args[1:]:
					s += func(j, "",gdic, ldic)
			s += ";\n"
		else:
			s += func(i.targets[0], "", gdic, ldic) + " = " + func(i.value, "", gdic, ldic) + ";\n"

	elif type(i) == ast.Call:
		# process some special funcs
		if i.func.id == "dcl":
			# processed in ast.Assign.
			pass
		elif i.func.id == "cast":
			s += "("
			s += func(i.args[0], "", gdic, ldic)
			s += ")" + func(i.args[1], "", gdic, ldic)
		elif i.func.id == "P":
			s += func(i.args[0], "", gdic, ldic) + " *"
		elif i.func.id == "const":
			s += "const " + func(i.args[0], "", gdic, ldic)
		
		#process other funcs
		elif hasattr(i.func, "id"):
			s += i.func.id + "("
			for j in i.args:
				s += func(j, "", gdic, ldic) + ", "
			if len(i.args):
				s = s[:-2]
			s += ")"
		else:
			# s += func(i.func)
			for j in i.args:
				s += func(j, "", gdic, ldic) + ", "
			if len(i.args):
				s = s[:-2]
			s += ")"
			print("ATTR????")
	
	elif type(i) == ast.Attribute:
		print("##### CAUTION #####\noioi\npointer dousundayo")
		s += func(i.value, "", gdic, ldic) + "->" + i.attr

	elif type(i) == ast.Name:
		if i.id == "self":
			s += "this"
		else:
			s += i.id

	elif type(i) == ast.Num:
		s += str(i.n)
	
	elif type(i) == ast.Str:
		s += '"' + i.s + '"'
	
	elif type(i) == ast.NameConstant:
		s += str(i.value)
	
	elif type(i) == ast.Return:
		s += "return"
		if i.value:
			s += " " + func(i.value, "", gdic, ldic)
		s += ";\n"
	
	elif type(i) == ast.Delete:
		s += "delete " + func(i.targets[0], "", gdic, ldic) + ";\n"
	
	elif type(i) == ast.While:
		s += "while(" + func(i.test, "", gdic, ldic) + "){\n"
		for j in i.body:
			s += func(j, "", gdic, ldic)
		s += "}\n"
	
	elif type(i) == ast.For:
		s += "for(int " + i.target.id + "=" + func(i.iter.args[0], "", gdic, ldic) + " ; "
		s += i.target.id + "<" + func(i.iter.args[1], "", gdic, ldic) + " ; "
		s += i.target.id + "++){\n"
		for j in i.body:
			s += func(j, "", gdic, ldic)
		s += "}\n"
	
	elif type(i) == ast.If:
		s += "if(" + func(i.test, "", gdic, ldic) + "){\n"
		for j in i.body:
			s += func(j, "", gdic, ldic)
		s += "}\n"
		if i.orelse:
			if type(i.orelse[0]) == ast.If:
				s += "else " + func(i.orelse[0], "", gdic, ldic)
			else:
				s += "else{\n"
				for j in i.orelse:
					s += func(j, "", gdic, ldic)
				s += "}\n"
	
	elif type(i) == ast.AugAssign:
		op = ""
		if type(i.op) == ast.Add:
			op = " += "
		elif type(i.op) == ast.Sub:
			op = " -= "
		elif type(i.op) == ast.Mult:
			op = " *= "
		else:
			print("Implement ! : " + str(i.op))
		
		s += func(i.target, "", gdic, ldic) + op + func(i.value, "", gdic, ldic) + ";\n"
		
	elif type(i) == ast.BinOp:
		op = ""
		if type(i.op) == ast.Mult:
			op = "*"
		elif type(i.op) == ast.Add:
			op = "+"
		elif type(i.op) == ast.Sub:
			op = "-"
		elif type(i.op) == ast.FloorDiv:
			op = "/"
		elif type(i.op) == ast.Mod:
			op = "%"
		elif type(i.op) == ast.BitOr:
			op = "|"
		elif type(i.op) == ast.BitAnd:
			op = "&"
		else:
			print("Implement the Operator! : " + str(i.op))
		
		s += "(" + func(i.left, "", gdic, ldic) + " " + op + " " + func(i.right, "", gdic, ldic) + ")"
	
	elif type(i) == ast.Compare:
		op = ""
		if type(i.ops[0]) == ast.Eq:
			op = " == "
		elif type(i.ops[0]) == ast.NotEq:
			op = " != "
		elif type(i.ops[0]) == ast.Lt:
			op = " < "
		elif type(i.ops[0]) == ast.LtE:
			op = " <= "
		elif type(i.ops[0]) == ast.Gt:
			op = " > "
		elif type(i.ops[0]) == ast.GtE:
			op = " >= "
		else:
			print("IMPLEMENT??? : " + str(i.op))
		
		s += func(i.left, "", gdic, ldic) + op + func(i.comparators[0], "", gdic, ldic)
	
	elif type(i) == ast.BoolOp:
		op = ""
		if type(i.op) == ast.And:
			op = " && "
		elif type(i.op) == ast.Or:
			op = " || "
		else:
			print("Implement!!! : " + str(i.op))
		
		s += func(i.values[0], "", gdic, ldic) + op + func(i.values[1], "", gdic, ldic)
	
	elif type(i) == ast.Pass:
		pass
	
	elif type(i) == ast.Break:
		s += "break;\n"
	
	elif type(i) == ast.Continue:
		s += "continue;\n"
	
	else:
		print("Not Yet! : " + str(i))

	return s


def beautiful_c(s):
	lines = s.split("\n")
	rslt = ""
	
	# indent level
	lv = 0
	for i in lines:
		if i.find("{") != -1:
			for j in range(0, lv):
				rslt += "\t"
			rslt += i + "\n"
			lv += 1
			
		elif i.find("}") != -1:
			lv -= 1
			for j in range(0, lv):
				rslt += "\t"
			rslt += i + "\n"
		elif len(i) and i[-1] == ":":
			for j in range(0, lv - 1):
				rslt += "\t"
			rslt += i + "\n"
		else:
			for j in range(0, lv):
				rslt += "\t"
			rslt += i + "\n"
			
	return rslt


"""
def _get_attr_chain_c_code(base_attr, gdic, ldic):
	arr = [base_attr]
	node = base_attr.value
	while True:
		if type(node) == ast.Name:
			arr.append(node)
			break
		elif type(node) == ast.Attribute:
			arr.append(node)
		elif type(node) == ast.Call:
			arr.append(node)
			if type(node.func) == ast.Name:
				break
			elif type(node.func) == ast.Attribute:
				node = node.func
			else:
				print("SGF+FSDFFGOJJGSROJGOJTOHOTJHOJTS!!!")
		
		node = node.value
	
	arr.reverse()
	
	# OK! From dictionaries, now we can judge attributes are selected properly or not.
	# Do it!
	# By the way, some complexed example will be helpful for a better implementation.
	
	# obj.x.getX(obj.parent.getPrevTr().x).bone
	
	# That is, attr chains, recursive. Very interesting.
	curtype = ""
	for i in arr:
		if type(i) == ast.Name:
			if i.id in ldic:
				print("LDIC!" + str(i.id))
				curtype = i.id
			elif i.id in gdic:
				print("GDIC!" + str(i.id))
				curtype = i.id
			else:
				print("ERR!!!!!" + str(i.id))
		elif type(i) == ast.Attribute:
			pass
		# if type(i) == ast.Name:
		# 	curtype = get_type_yeah(i, gdic, ldic)
		# 	if is_pointer_type(curtype):
		# 		i.is_pointer = True
		# 	else:
		# 		i.is_pointer = False
		pass
	return arr
	

def _check_has_attr(clsname, attr, gdic):
	if clsname in gdic:
		for i in gdic[clsname]["vars"]:
			if i[0] == attr:
				return i[1]
		for i in gdic[clsname]["methods"]:
			if i.name:
				return i.returns.id
	
	raise Exception("NAI!!!!!NAI!!!!!!!!!!!")
	
"""
if __name__ == '__main__':
	testy = _get_node("""
def fire(a: P(int), b: float)->void:
	f = dcl(float, 8.0)
	f = 8.8 + 87.8 * 5.6
	while True or False:
		f *= 1
		print("Yahoo")
	for i in range(0, 7):
		f += 414
		f += 555
		while True:
			f += 5
			break
	if True:
		print(a(8,4,2).b.cv)
	return f
	del a
	if 5 < funcy(8, 73):
		print("GHAG")
	elif 4.1415:
		a(a)
	elif 525252:
		a(52525)
	else:
		print(cast(const(P(int)), fire))
		print(444)
""")
	
	tmpdic = _get_globals(testy)
	gdic.update(tmpdic)
	
	rslt = _get_funcdef_c_code(testy.body[0], gdic)
	print("\n\n\n")
	print(beautiful_c(rslt))
	
	nodes = ast.parse("""
class Mokkori(Fire, Uhhoi):
	def __init__(self, a: str)->int:
		self.x = dcl(Float)
		self.y = dcl(Float)
		self.cnt = dcl(Int)
	def show(self)->int:
		continue
""")
	tmpdic = _get_globals(nodes)
	gdic.update(tmpdic)
	_get_classdef_c_code(nodes.body[0], gdic)
	for i in gdic:print(i)
	# print(beautiful_c(_get_classdef_c_code(nodes.body[0])))
	# print(_get_attr_chain_c_code(ast.parse("a.b.func(6,7,4).tr.size").body[0].value, {}, {}))

