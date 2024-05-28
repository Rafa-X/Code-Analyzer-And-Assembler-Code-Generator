from tkinter import *
from tkinter import ttk, messagebox
from enum import Enum
from tkinter import filedialog
import re
import ply.yacc as yacc
import ply.lex as lex

lexico = []  # list for the recognized tokens
sintactico = []  # list for the sintax tree generated
funciones = []  # list for all the secondary functions names declared

sintacErrorFlag = False  # flag to indicate a sintax error appeared
semanticErrorFlag = False
erroresSintactico = []  # list for all the sintax errors (if found)
erroresSemantico = []  # list for all the semantic errors (if found)

linea = 0  # line count during the analysis
corchetes = 0  # bracket count for the sintax analysis


class Lexema():
    def __init__(self, data, IDtoken, token):
        super().__init__()
        self.data = data
        self.IDtoken = IDtoken
        self.token = token


# ////////////////////////////////////////////////// TOKEN DEFINITION
class Token(Enum):  # tokens enumerados en orden 0-23
    IDENTIFICADOR = 0  # letras y/o digitos
    ENTERO = 1
    REAL = 2
    CADENA = 3  # tipo de dato
    TIPO_DATO_FUNCION = 4  # tipo de dato y visibilidad de funciones - int, float, void,
    SUMA_RESTA = 5
    MUL_DIV = 6
    RELACIONAL = 7  # operadores relacionales
    OR = 8  # operador or
    AND = 9  # operador and
    NOT = 10  # operador not
    IGUALDAD = 11  # operadores igualdad & distinto
    PUNTO_COMA = 12
    COMA = 13
    PARENTESIS_IZQ = 14
    PARENTESIS_DER = 15
    CORCHETE_IZQ = 16
    CORCHETE_DER = 17
    ASIGNACION = 18  # asignacion de datos -> =
    RESERVADA_IF = 19
    RESERVADA_WHILE = 20
    RESERVADA_RETURN = 21
    RESERVADA_ELSE = 22
    SIMBOLO_PESOS = 23


# tokens definitions
tokens = ('IDENTIFICADOR', 'ENTERO', 'REAL', 'CADENA', 'TIPO_DATO_FUNCION',
          'SUMA', 'RESTA', 'MUL', 'DIV', 'RELACIONAL', 'OR', 'AND', 'NOT', 'PUNTO_COMA', 'COMA',
          'PARENTESIS_IZQ', 'PARENTESIS_DER', 'ASSIGN', 'CORCHETE_IZQ', 'CORCHETE_DER',
          'RESERVADAS')

# rules for tokens
t_SUMA = r'\+'
t_RESTA = r'\-'
t_MUL = r'\*'
t_DIV = r'\/'
t_AND = r'\&\&'
t_OR = r'\|\|'
t_PUNTO_COMA = r'\;'
t_COMA = r'\,'
t_PARENTESIS_IZQ = r'\('
t_PARENTESIS_DER = r'\)'
t_ASSIGN = r'\='
t_CORCHETE_IZQ = r'\{'
t_CORCHETE_DER = r'\}'

# Ignorar caracteres en blanco y tabulaciones
t_ignore = ' \t'


def t_error(t):  # rule to handle errors
    print(f"Error léxico: Carácter inesperado '{t.value[0]}' en la linea " + str(linea))
    t.lexer.skip(1)


def t_REAL(t):
    r'\d+\.[0-9]*'
    return t


def t_ENTERO(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_TIPO_DATO_FUNCION(t):
    r'int|float|string|void|main'
    return t


def t_RESERVADAS(t):
    r'if|else|while|return'
    return t


def t_CADENA(t):
    r"'[a-zA-Z]+([a-zA-Z0-9])*'"
    t.value = float(t.value)
    return t


def t_IDENTIFICADOR(t):
    r'[a-zA-Z]+([a-zA-Z0-9])*'
    return t


def t_RELACIONAL(t):
    r'<|>|<=|>=|!=|=='
    return t


# builds the lexical analyzer
lexer = lex.lex()


# ////////////////////////////////////////////////// grammar definition
def p_program(p):
    '''
    program : datatype_function datatype_function symbol symbol symbol
            | assignment
            | function
            | conditional
            | symbol
    '''
    if (p[1] == 'int' or p[1] == 'void') and p[2] == 'main':
        p[0] = tuple(p[1:])  # main
    else:
        p[0] = p[1]


def p_assignment(p):
    '''
    assignment : IDENTIFICADOR symbol expression symbol
               | datatype_function IDENTIFICADOR symbol
               | datatype_function IDENTIFICADOR symbol expression symbol
               | IDENTIFICADOR symbol function
    '''
    if len(p) == 5 and p[2] == '=' and p[4] == ';':
        p[0] = ('=', p[1], p[3], p[4])  # assignment
    elif len(p) == 4 and (p[1] == 'int' or p[1] == 'float' or p[1] == 'string') and p[3] == ';':
        p[0] = (p[1], p[2], p[3])  # declaration
    elif len(p) == 6 and (p[1] == 'int' or p[1] == 'float' or p[1] == 'string') and p[3] == '=' and p[5] == ';':
        p[0] = (p[1], '=', p[2], p[4], p[5])  # declaration and assignment
    else:
        # p[0] = tuple(p[1:])
        p[0] = (p[2], p[1], tuple(p[3:]))


def p_function(p):
    '''
    function : IDENTIFICADOR symbol IDENTIFICADOR symbol symbol
             | IDENTIFICADOR symbol IDENTIFICADOR symbol IDENTIFICADOR symbol symbol
             | IDENTIFICADOR symbol IDENTIFICADOR symbol IDENTIFICADOR symbol IDENTIFICADOR symbol symbol
             | datatype_function IDENTIFICADOR symbol datatype_function IDENTIFICADOR symbol symbol
             | datatype_function IDENTIFICADOR symbol datatype_function IDENTIFICADOR symbol datatype_function IDENTIFICADOR symbol symbol
             | datatype_function IDENTIFICADOR symbol datatype_function IDENTIFICADOR symbol datatype_function IDENTIFICADOR symbol datatype_function IDENTIFICADOR symbol symbol
    '''
    global funciones
    if p[1] in funciones:
        p[0] = tuple(p[1:])
    if p[2] != 'main' and p[3] == '(':
        if len(p) == 8 and p[6] == ')' and p[7] == '{':
            funciones.append(p[2])  # add the function name to the functions list
            p[0] = tuple(p[1:])
        elif len(p) == 11 and p[6] == ',' and p[9] == ')' and p[10] == '{':
            funciones.append(p[2])  # add the function name to the functions list
            # p[0] = (p[1], p[2], p[4], p[5], p[6], p[7])
            p[0] = tuple(p[1:])
        elif len(p) == 14 and p[6] == ',' and p[9] == ',' and p[12] == ')' and p[13] == '{':
            funciones.append(p[2])  # add the function name to the functions list
            p[0] = tuple(p[1:])


def p_conditional(p):
    '''
    conditional : RESERVADAS symbol evaluation symbol symbol
                | RESERVADAS symbol
                | RESERVADAS IDENTIFICADOR symbol
    '''
    if p[1] == 'if' and p[2] == '(' and p[4] == ')' and p[5] == '{':
        p[0] = tuple(p[1:])
    elif (p[1] == 'else' and p[2] == '{'):
        p[0] = tuple(p[1:])
    elif p[1] == 'return' and (p[2] == ';' or p[3] == ';'):
        p[0] = tuple(p[1:])


def p_evaluation(p):
    '''
    evaluation : NOT expression
               | expression AND expression
               | expression OR  expression
               | expression RELACIONAL expression
    '''
    if p[1] == 'NOT':
        p[0] = (p[1], p[2])
        lexico.append(Lexema(p[1], Token.NOT, "Operador NOT"))
    elif p[1] == 'AND':
        p[0] = (p[2], p[1], p[3])
        lexico.append(Lexema(p[2], Token.AND, "Operador AND"))
    elif p[1] == 'OR':
        p[0] = (p[2], p[1], p[3])
        lexico.append(Lexema(p[2], Token.OR, "Operador OR"))
    else:
        p[0] = (p[2], p[1], p[3])  # engloba AND, OR y RELACIONAL
        lexico.append(Lexema(p[2], Token.RELACIONAL, "Operador relacional"))


def p_expression(p):
    '''
    expression : factor
               | expression RESTA expression
               | expression SUMA  expression
               | expression MUL   expression
               | expression DIV   expression
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '+':
        p[0] = ('+', p[1], p[3])
        lexico.append(Lexema(p[1], Token.SUMA_RESTA, "Operador suma"))
    elif p[2] == '-':
        p[0] = ('-', p[1], p[3])
        lexico.append(Lexema(p[1], Token.SUMA_RESTA, "Operador resta"))
    elif p[2] == '*':
        p[0] = ('*', p[1], p[3])
        lexico.append(Lexema(p[1], Token.MUL_DIV, "Operador multiplicacion"))
    elif p[2] == '/':
        p[0] = ('/', p[1], p[3])
        lexico.append(Lexema(p[1], Token.MUL_DIV, "Operador division"))


def p_factor(p):
    '''
    factor : ENTERO
           | REAL
           | CADENA
           | IDENTIFICADOR
           | symbol expression symbol
    '''
    if len(p) == 2 and type(p[1]) == int:
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.ENTERO, "Variable entero"))
    elif len(p) == 2 and type(p[1]) == float:
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.REAL, "Variable flotante"))
    elif len(p) == 2 and re.search('^"[a-zA-Z0-9]"', p[1]):
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.CADENA, "Variable cadena"))
    elif len(p) == 2 and type(p[1]) == str:
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.IDENTIFICADOR, "Identificador"))
    elif p[1] == '(' and p[3] == ')':
        p[0] = p[2]


def p_datatype_function(p):
    '''
    datatype_function : TIPO_DATO_FUNCION
    '''
    if (p[1] == 'int'):
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.TIPO_DATO_FUNCION, "Palabra reservada int"))
    elif (p[1] == 'float'):
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.TIPO_DATO_FUNCION, "Palabra reservada float"))
    elif (p[1] == 'string'):
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.TIPO_DATO_FUNCION, "Palabra reservada string"))
    elif (p[1] == 'void'):
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.TIPO_DATO_FUNCION, "Palabra reservada void"))
    elif (p[1] == 'main'):
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.TIPO_DATO_FUNCION, "Palabra reservada main"))


def p_symbol(p):
    '''
    symbol : PARENTESIS_IZQ
           | PARENTESIS_DER
           | CORCHETE_IZQ
           | CORCHETE_DER
           | PUNTO_COMA
           | COMA
           | ASSIGN
    '''
    global corchetes  # when brackets appear counts it to keep a correct sintax
    if p[1] == '(':
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.PARENTESIS_IZQ, "Parentesis izquierdo"))
    elif p[1] == ')':
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.PARENTESIS_DER, "Parentesis derecho"))
    elif p[1] == '{':
        corchetes += 1  # add bracket count
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.CORCHETE_IZQ, "Corchete izquierdo"))
    elif p[1] == '}':
        corchetes -= 1  # sub bracket count
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.CORCHETE_DER, "Corchete derecho"))
    elif p[1] == ';':
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.PUNTO_COMA, "Punto y coma"))
    elif p[1] == ',':
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.COMA, "Coma"))
    elif p[1] == '=':
        p[0] = p[1]
        lexico.append(Lexema(p[1], Token.ASIGNACION, "Asignacion"))


# rule to handle sintax errors
def p_error(p):
    global linea
    global corchetes
    global sintacErrorFlag
    global erroresSintactico
    sintacErrorFlag = True

    if p:
        erroresSintactico.append(f"Error sintáctico en '{p.value}' Linea {linea}\n")
    else:
        erroresSintactico.append(f"Error sintáctico: Fin de entrada inesperado. Linea {linea}\n")
        return
    if corchetes > 0:
        erroresSintactico.append(f"Fin de expresion invalida: corchetes faltantes.\n")


# ////////////////////////////////////////////////// LEXICAL AND SYNTACTIC
parser = yacc.yacc()


def analyze_expression(expression):  # parse one or more expressions and show the syntax tree
    result = parser.parse(expression)

    sintactico.append(result)  # store the structure of the sintax tree
    print("Árbol sintáctico:", result)  # prints the sintax tree


# ////////////////////////////////////////////////// SEMANTIC
def analizadorSemantico():
    functions = []   #list of lists to save for separate all the functions
    parameters = []  #parameters given to functions, type  var_name -> int num
    vars = []        #vars in the code, type  var_name  value -> int num 1
    lineCount = 0  #count for the lines evaluated
    activeConditional = False

    getFunctions(functions)     #get by separate all the functions
    for function in functions:  #get function
        for line in function:   #iterate line per line
            lineCount += 1
            if line == '}': continue  #ignore the character

            #////// get the functions parameters given -> type  var_name
            if line == function[0] and line[2] != 'main': getParameters(parameters, line)  

            #////// var declaration -> type  var_name  value
            if (line[0] == 'int' or line[0] == 'float') and line[-1] != '{':  
                activeConditional = False  #sets that the conditional (if apply) isn't empty
                vars.append([line[0], line[1], None])
            if line[0] == 'str' and line[-1] != '{':
                activeConditional = False  #sets that the conditional (if apply) isn't empty
                vars.append([line[0], line[1], ""])
        
            #////// var assignation
            if line[0] == '=':  
                activeConditional = False  #sets that the conditional (if apply) isn't empty
                mainvar = getVarParameter(line[1], vars, parameters)  #var to be assigned
                if mainvar == None: 
                    errorInexistentAssign(lineCount, line[1])  #the var isn't declared previously
                    return
                var = validateAssignsType(line, mainvar, vars, parameters, functions)  #evaluate the assignment variables types
                if var != None:
                    errorDataType(lineCount, var)  #one or more variables don't have the correct type

            #//////
            '''if line[0] == 'return':
                var = getVarParameter(line[1], vars, parameters)
                checkFunctionType(var[1], maintype, functions)'''
                    
            #////// conditional
            if activeConditional == True:
                errorConditionalEmpty(lineCount)  #means it make a round with the flag and don't recognize any instruction inside the conditional
            if line[0] == 'if':  
                activeConditional = True
                var = validateConditionals(line[2], vars, parameters)
                if var != None:
                    #if var[2] == None: errorComparisonValues(lineCount, var[1])  #a variable doesn't have a value to compare with
                    errorComparisonDatatype(lineCount, var)  #one or more variables don't have the correct type
            elif line[0] == 'else':
                activeConditional = True

#/// SEMANTIC AUXILIAR FUNCTIONS
def getFunctions(funciones):
    i = 0
    idx = 0  #index for the functions
    brackets = 0  #count for the inner brackets
    longS = len(sintactico)

    while i < longS:
        line = sintactico[i]
        if (line[0] == 'int' or line[0] == 'float' or line[0] == 'str' or line[0] == 'void') and line[-1] == '{':
            funciones.append([])  #add a new sublist for the incoming function
            brackets += 1
            while brackets >= 1:
                funciones[idx].append(line)  #add the line in X pos because its inside of one function
                i += 1  #increase the index for the lines
                line = sintactico[i]

                if line == None: continue
                if line[-1] == '{': brackets += 1
                if line[-1] == '}': brackets -= 1

            #exit the loop means the function has reached its very end
            funciones[idx].append(line)
            idx += 1  #index for the next function
            i += 1

def getParameters(parameters, line):
    if len(line) == 7:
        parameters.append([line[3], line[4]])
    elif len(line) == 10:
        parameters.append([line[3], line[4]])
        parameters.append([line[6], line[7]])
    elif len(line) == 13:
        parameters.append([line[3], line[4]])
        parameters.append([line[6], line[7]])
        parameters.append([line[9], line[10]])

def getVarParameter(varname, vars, parameters):  #get the var declarated from a given name
    for var in vars:
        if varname == var[1]:
            return var  #value of the var
    for par in parameters:
        if varname == par[1]:
            return par  #value of the var
    return None

def checkFunctionType(element, maintype, functions):
    for function in functions:
        if function[0][1] == element and function[0][0] == maintype:
            return function[0][0]
    return None

def validateAssignsType(line, mainvar, vars, parameters, functions):
    maintype = mainvar[0]
    if len(line) > 1: 
        if mainvar[1] == line[1]: line = line[2:]  #removes the mainvar to avoid extra evaluations
    for element in line:
        if element == ';' or element == '(' or element == ')' or element == ',': continue  #ignore characters
        
        #there is a tuple inside of assignation
        if isinstance(element, tuple): 
            if (var := validateAssignsType(element, mainvar, vars, parameters, functions)) != None:  #recursivity evaluation
                return var  #the vars types are different = ERROR
        else: 
            #evaluate int values, float values
            if (re.fullmatch(r'[0-9]+', str(element)) is not None or 
                re.fullmatch(r'\d+\.[0-9]*', element)) is not None:
                if maintype != type(element).__name__:
                    return element  #the vars types are different = ERROR
            
            #evaluate variables
            elif re.fullmatch(r'[a-zA-Z0-9]+', element) is not None:
                auxvar1 = getVarParameter(element, vars, parameters)  #get variables parameters
                if auxvar1 == None: 
                    auxvar2 = checkFunctionType(element, maintype, functions)  #get functions types
                    if maintype != auxvar2:
                        return auxvar2  #the vars types are different = ERROR
                else:
                    if maintype != auxvar1[0]:
                        return auxvar1[1]  #the vars types are different = ERROR
                

        #evaluate return value from a function
    return None  #the vars types are the same = VALID

def validateConditionals(line, vars, parameters):
    maintype = None
    for element in line:
        if element == ';' or element == '(' or element == ')' or element == ',': continue  #ignore characters

        #evaluate variables
        if re.fullmatch(r'[a-zA-Z0-9]+', element) is not None:
            auxvar = getVarParameter(element, vars, parameters)  #get variables parameters
            if maintype == None:
                maintype = auxvar[0]
            else:
                if maintype != auxvar[0]:
                    return auxvar[1]
    return None

def errorFunctionDeclaration(linea):
    global semanticErrorFlag
    semanticErrorFlag = True
    erroresSemantico.append(f"Declaracion de funcion contiene uno o mas elementos ilegales. Linea {linea}")

def errorDataType(linea, varname):
    global semanticErrorFlag
    semanticErrorFlag = True
    erroresSemantico.append(f"Asignacion invalida en {varname}, tipo de dato incorrecto. Linea {linea}")

def errorInexistentAssign(linea, varname):
    global semanticErrorFlag
    semanticErrorFlag = True
    erroresSemantico.append(f"La variable -{varname}- no ha sido declarada. Linea {linea}")

def errorComparisonDatatype(linea, varname):
    global semanticErrorFlag
    semanticErrorFlag = True
    erroresSemantico.append(f"Comparacion invalida en {varname}, tipos de dato de variables incompatibles. Linea {linea}")

def errorComparisonValues(linea, varname):
    global semanticErrorFlag
    semanticErrorFlag = True
    erroresSemantico.append(f"Comparacion invalida en {varname}, la variable no tiene asignado un valor. Linea {linea}")

def errorConditionalEmpty(linea):
    global semanticErrorFlag
    semanticErrorFlag = True
    erroresSemantico.append(f"Bloque condicional invalido, se encuentra vacio. Linea {linea}")


# ////////////////////////////////////////////////// IU
class Application(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.grid(sticky="n")

        self.lineas = []  # code lines obtained from .txt

        # Create a Treeview for the Lexic table
        self.lex = ttk.Treeview(self, columns=("Lexema", "Token", "#"), show="headings")
        self.lex.heading("Lexema", text="Lexema")
        self.lex.column("Lexema", width=150)
        self.lex.heading("Token", text="Token")
        self.lex.column("Token", width=150)
        self.lex.heading("#", text="# Token")
        self.lex.column("#", width=100)
        self.lex.place(x=530, y=10, width=650, height=240)

        # sintax errors area
        self.label1 = Label(self, text="Sintax Errors", border=1, relief="solid")
        self.label1.place(x=10, y=270)
        self.sintaxErrorArea = Text(self, width=62, height=8, relief="solid")
        self.sintaxErrorArea.place(x=10, y=285)

        # semantic errors area
        self.label2 = Label(self, text="Semantic Errors", border=1, relief="solid")
        self.label2.place(x=10, y=430)
        self.semanticErrorArea = Text(self, width=62, height=8, relief="solid")
        self.semanticErrorArea.place(x=10, y=445)

        # functions buttons
        self.abrir = Button(self, text="Abrir Fuente", width=25, command=self.abrirTxt, background="#4C95ED")
        self.abrir.place(x=10, y=620)
        self.text_area = Text(self, height=15, width=62, relief="solid")
        self.text_area.place(x=10, y=10)
        self.abrir = Button(self, text="Analizador Lexico y Sintactico", width=25, command=self.analizadorSintactico,
                            background="#4C95ED")
        self.abrir.place(x=250, y=620)
        self.abrir = Button(self, text="Generar ASM", width=25, command=self.generarasm, background="#4C95ED")
        self.abrir.place(x=10, y=660)

        # Create a Canvas for the Syntax tree
        self.canvas = Canvas(self, bg="white", width=650, height=450)
        self.canvas.place(x=530, y=260)

    def abrirTxt(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filepath:
            return

        with open(filepath, "r") as file:
            self.lineas = file.readlines()

        self.text_area.delete(1.0, END)
        self.text_area.insert(END, ''.join(self.lineas))

    # //////////////////////////////
    def analizadorSintactico(self):
        contenido = self.text_area.get("1.0", "end-1c")
        self.lineas.clear()
        self.lineas.extend(contenido.split('\n'))
        self.text_area.delete(1.0, END)
        self.text_area.insert(END, '\n'.join(self.lineas))

        global linea  # indicates the ucse of a globar var
        global error
        global sintacErrorFlag
        global semanticErrorFlag
        lexico.clear()
        linea = 0
        error = ""
        sintacErrorFlag = False

        for L in self.lineas:  # makes the lexical and sintactical analysis
            linea += 1
            if L != "":
                analyze_expression(L)

        for item in self.lex.get_children():  # clean lexical area
            self.lex.delete(item)
            self.lex.update()
        self.sintaxErrorArea.delete(1.0, END)  # clean error area
        self.semanticErrorArea.delete(1.0, END)

        for i, lexema in enumerate(lexico, start=1):
            self.lex.insert("", "end", values=(lexema.data, lexema.token, lexema.IDtoken.value))

        #show the errores if there were any
        if sintacErrorFlag:
            for error in erroresSintactico:
                self.sintaxErrorArea.insert(END, ''.join(error+"\n"))
        else:
            self.sintaxErrorArea.insert(END, ''.join("Analisis realizado sin errores."))
            # Draw the syntax tree if all were correct
            self.canvas.delete("all")

        #////////////////////////////// SINTAX TREE DRAWING
        analizadorSemantico() #makes the semantic analysis
        if semanticErrorFlag:
            for error in erroresSemantico:
                self.semanticErrorArea.insert(END, ''.join(error+"\n"))
        else:
            self.semanticErrorArea.insert(END, ''.join("Analisis realizado sin errores."))
            self.draw_syntax_tree_loop()

    # //////////////////////////////
    def draw_syntax_tree_loop(self, count=0):
        if count < len(sintactico):
            self.canvas.delete("all")
            self.draw_tree_node((200, 50), sintactico[count], level=1)
            self.after(1000, self.draw_syntax_tree_loop, count + 1)

    def draw_tree_node(self, position, node, level):
        x, y = position
        if isinstance(node, tuple):
            node_label = str(node[0])
        else:
            node_label = str(node)
        # Draw the node
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="white", outline="black")
        self.canvas.create_text(x, y, text=node_label)
        if isinstance(node, tuple) and len(node) > 1:  # Check if the node has children
            # Calculate the positions for child nodes
            num_children = len(node) - 1
            child_spacing = 100
            total_width = num_children * child_spacing
            start_x = x - total_width // 2
            y_offset = 100
            child_level = level + 1
            # Draw edges to child nodes and recursively draw child nodes
            for i, child_node in enumerate(node[1:], start=1):
                child_x = start_x + i * child_spacing
                child_y = y + y_offset * child_level / 2  # Adjust vertical position based on node level
                self.canvas.create_line(x, y, child_x, child_y, fill="black")
                # Recursively draw child nodes
                self.draw_tree_node((child_x, child_y), child_node, child_level)


    #////////////////////////////// ASSEMBLER CODE GENERATOR
    @staticmethod
    def generarasm():

        inside_main = False
        current_func = None
        funciones = {}

        asm_code = """
                   .data
                   """

        for element in sintactico:  # var declaration
            if element[0] == 'int' and len(element) == 3:
                asm_code += f"    {element[1]} DW 0\n"  # var declaration in main

        for element in sintactico:
            if element[0] == 'main' and element[1] == 'void':
                asm_code += "_start:\n"
                inside_main = True
            elif inside_main and element[0] == '{':
                asm_code += "; Inicio del bloque main\n"
            elif inside_main and element[0] == '}':
                asm_code += "    MOV AX, 0x4C00\n"
                asm_code += "    INT 21H\n"
                inside_main = False
            elif inside_main:
                if element[0] == 'int':
                    asm_code += f"    {element[1]} DW 0\n"  # var declaration in main
                elif element[0] == '=':
                    if isinstance(element[2], int):  # var declaration in main
                        asm_code += f"    MOV AX, {element[2]}\n"
                    else:
                        asm_code += f"    MOV AX, [{element[2]}]\n"
                    asm_code += f"    MOV [{element[1]}], AX\n"
                #////// handle of instruction IF
                elif element[0] == 'if':
                    asm_code += f"    MOV AX, [{element[2][1]}]\n"
                    asm_code += f"    CMP AX, [{element[2][2]}]\n"
                    asm_code += f"    JL menor_que_precio\n"
                #////// handle of instruction ELSE
                elif element[0] == 'else': 
                    asm_code += "    JMP fin\n"
                    asm_code += "menor_que_precio:\n"
                elif element[0] == 'promedio' and element[1] == '=':
                    if element[2][0] == 'calcula':
                        asm_code += f"    MOV AX, [{element[2][2]}]\n"
                        asm_code += f"    PUSH AX\n"
                        asm_code += f"    MOV AX, [{element[2][4]}]\n"
                        asm_code += f"    PUSH AX\n"
                        asm_code += f"    call calcula\n"
                        asm_code += f"    ADD sp, 4\n"
                        asm_code += f"    MOV [{element[0]}], AX\n"
                    elif element[2][0] == 'resta':
                        asm_code += "    ; Llamar a resta\n"
                        asm_code += f"    MOV AX, [{element[2][2]}]\n"
                        asm_code += f"    PUSH AX\n"
                        asm_code += f"    CALL resta\n"
                        asm_code += f"    ADD sp, 2\n"
                        asm_code += f"    MOV [{element[0]}], AX\n"
                    elif element[2][0] == '+':
                        asm_code += f"    MOV AX, [{element[2][1]}]\n"
                        asm_code += f"    ADD AX, [{element[2][2]}]\n"
                        asm_code += f"    MOV [{element[0]}], AX\n"
            else:
                #////// function definitions
                if element[0] == 'int' and element[1] not in ('main', 'res', 'subs'):
                    funciones[element[1]] = []
                    current_func = element[1]
                elif element[0] == '}' and current_func:
                    funciones[current_func].append('; Fin del bloque de la función\n')
                    current_func = None
                elif current_func:
                    funciones[current_func].append(element)

        for func_name, instructions in funciones.items():
            asm_code += f"{func_name}:\n"
            asm_code += "    PUSH bp\n"
            asm_code += "    MOV bp, sp\n"
            for instr in instructions:
                if instr[0] == '=':
                    if isinstance(instr[2], tuple):
                        if instr[2][0] == '+':
                            asm_code += f"    MOV AX, [bp+4]\n"
                            asm_code += f"    MOV BX, [bp+6]\n"
                            asm_code += f"    MOV AX, BX\n"
                            asm_code += f"    MOV [bp-2], AX\n"
                        elif instr[2][0] == '-':
                            asm_code += f"    MOV AX, [bp+4]\n"
                            asm_code += f"    SUB AX, {instr[2][2]}\n"
                            asm_code += f"    MOV [bp-2], AX\n"
                    else:
                        asm_code += f"    MOV AX, {instr[2]}\n"
                        asm_code += f"    MOV [bp-2], AX\n"
                elif instr[0] == 'return':
                    asm_code += f"    MOV AX, [bp-2]\n"
            asm_code += "    POP bp\n"
            asm_code += "    RET\n"

        asm_code += "fin:\n"
        asm_code += "    MOV AX, 0x4C00\n"
        asm_code += "    INT 21H\n"

        with open("Main.asm", "w") as file:
            file.write(asm_code)
        messagebox.showinfo("Generación de ASM", "Archivo ASM generado exitosamente")

# //////////////////////////////////////////////////
class TabbedApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabbed Interface")

        self.notebook = ttk.Notebook(self.root)

        self.tab1 = Frame(self.notebook)

        self.notebook.add(self.tab1, text="Subproducto 2")

        self.app_tab1 = Application(self.tab1)
        self.app_tab1.pack(fill="both", expand=True)

        self.notebook.pack(expand=True, fill="both")


if __name__ == '__main__':
    main_window = Tk()
    main_window.title("Subproducto 2")
    main_window.geometry("1200x800")
    app = TabbedApp(main_window)

    main_window.mainloop()
