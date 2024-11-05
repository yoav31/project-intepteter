import math
import ast
class Interpreter:
    def __init__(self):
        self.variables = {}
        self.dispatch = {
        # Basic arithmetic ops
        ast.Add: lambda x, y: x + y,
        ast.Sub: lambda x, y: x - y,
        ast.Mult: lambda x, y: x * y,
        ast.Div: lambda x, y: x / y,
        # Comparisons
        ast.Gt: lambda x, y: x > y if x is not None and y is not None else False,
        ast.Lt: lambda x, y: x < y if x is not None and y is not None else False,
        ast.GtE: lambda x, y: x >= y if x is not None and y is not None else False,
        ast.LtE: lambda x, y: x <= y if x is not None and y is not None else False,
        ast.Eq: lambda x, y: x == y,
        ast.NotEq: lambda x, y: x != y,
        # Logical ops
        ast.And: lambda x, y: x and y,
        ast.Or: lambda x, y: x or y,
        # Advanced arithmetic ops
        ast.Mod: lambda x, y: x % y,
        ast.Pow: lambda x, y: x ** y,
        ast.FloorDiv: lambda x, y: x // y,
    }


    def tokenize_code(self, code):
        tree = ast.parse(code)
        tokens = []
        
        def visit_node(node):
            if isinstance(node, ast.Constant):
                tokens.append(('CONSTANT', node.value))
            elif isinstance(node, ast.Name):
                tokens.append(('NAME', node.id))
            elif isinstance(node, ast.BinOp):
                tokens.append(('OP', type(node.op).__name__))
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    tokens.append(('COMPARE', type(op).__name__))
            elif isinstance(node, ast.BoolOp):
                tokens.append(('BOOL_OP', type(node.op).__name__))
            elif isinstance(node, ast.UnaryOp):
                tokens.append(('UNARY_OP', type(node.op).__name__))
            elif isinstance(node, ast.Assign):
                tokens.append(('ASSIGN', '=')) 
            elif isinstance(node, ast.If):
                tokens.append(('IF', 'if'))
            elif isinstance(node, ast.For):
                tokens.append(('FOR', 'for'))
            elif isinstance(node, ast.While):
                tokens.append(('WHILE', 'while'))
            elif isinstance(node, ast.Call):
                tokens.append(('CALL', 'call'))
            elif isinstance(node, ast.Attribute):
                tokens.append(('ATTRIBUTE', node.attr))
            elif isinstance(node, ast.Expr):
                tokens.append(('EXPR', 'expression'))
            elif isinstance(node, ast.Subscript):
                tokens.append(('SUBSCRIPT', 'subscript'))
            elif isinstance(node, ast.List):
                tokens.append(('LIST', 'list'))
            elif isinstance(node, ast.Tuple):
                tokens.append(('TUPLE', 'tuple'))
            elif isinstance(node, ast.Dict):
                tokens.append(('DICT', 'dict'))
            elif isinstance(node, ast.Slice):
                tokens.append(('SLICE', 'slice'))
            elif isinstance(node, ast.Break):
                tokens.append(('BREAK', 'break'))
            elif isinstance(node, ast.Continue):
                tokens.append(('CONTINUE', 'continue'))
            elif isinstance(node, ast.Delete):
                tokens.append(('REMOVE', 'remove'))
            for child in ast.iter_child_nodes(node):
                visit_node(child)
            
        visit_node(tree)
        return tokens

    def eval(self, node):
        # Constants
        if isinstance(node, ast.Constant):
            return node.value
        
        # Variables Name
        elif isinstance(node, ast.Name):
            return self.variables.get(node.id)
        
        # Binary Operations
        elif isinstance(node, ast.BinOp):  # for two objects operation (2+3)
            left = self.eval(node.left)
            right = self.eval(node.right)
            if left is None or right is None: 
                return None
            return self.dispatch[type(node.op)](left, right)
        
        # Comparison
        elif isinstance(node, ast.Compare):
            left = self.eval(node.left)
            for op, right in zip(node.ops, node.comparators): # compares between every operands and their comparators
                right_val = self.eval(right)
                if not self.dispatch[type(op)](left, right_val):
                    return False  
                left = right_val
            return True
        
        # Logical Operations
        elif isinstance(node, ast.BoolOp):
            values = [self.eval(value) for value in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            elif isinstance(node.op, ast.Or):
                return any(values)
        
        # Assignment
        elif isinstance(node, ast.Assign):
            value = self.eval(node.value)
            for target in node.targets:
                self.assign(target, value)
            return value
        
        # If-statements
        elif isinstance(node, ast.If):
            if self.eval(node.test):
                return self.eval_body(node.body)
            elif node.orelse:
                return self.eval_body(node.orelse)
        
        # Expressions
        elif isinstance(node, ast.Expr):
            return self.eval(node.value)
        
        # Callables
        elif isinstance(node, ast.Call):    # calls for a func, and args are the args of the func
            func = self.eval(node.func)
            args = [self.eval(arg) for arg in node.args]
            if callable(func):
                return func(*args)
            else:
                raise TypeError(f"{func} is not callable")

        
        # Lists
        elif isinstance(node, ast.List):
            return [self.eval(elt) for elt in node.elts]
        
        # Tuples
        elif isinstance(node, ast.Tuple):
            return tuple(self.eval(elt) for elt in node.elts)
        
        # Dictionaries
        elif isinstance(node, ast.Dict):
            return {self.eval(key): self.eval(value) for key, value in zip(node.keys, node.values)}
        
        # Subscript
        elif isinstance(node, ast.Subscript): 
            value = self.eval(node.value)   # Evaluates the object being subscripted (the list or dictionary)
            if value is None:
                return None
            if isinstance(node.slice, ast.Index):       # Check if the subscript is an index 
                index = self.eval(node.slice.value)     # Evaluates the index
            elif isinstance(node.slice, ast.Slice):     # If the subscript is a slice 
                lower = self.eval(node.slice.lower) if node.slice.lower else None   # Evaluate the lower bound of the slice
                upper = self.eval(node.slice.upper) if node.slice.upper else None   # Evaluate the upper bound of the slice 
                step = self.eval(node.slice.step) if node.slice.step else None      # Evaluate the step of the slice 
                # Create a Python slice object using the evaluated bounds and step
                index = slice(lower, upper, step)
            # If the subscript is neither an index nor a slice, evaluate it directly
            else:
                index = self.eval(node.slice)
            # Try to access the value using the computed index/slice
            try:
                return value[index]
            except (IndexError, KeyError, TypeError):
                return None

        # Slice 
        elif isinstance(node, ast.Slice):
            lower = self.eval(node.lower) if node.lower else None
            upper = self.eval(node.upper) if node.upper else None
            step = self.eval(node.step) if node.step else None
            return slice(lower, upper, step)
        
        # Unary Ops
        elif isinstance(node, ast.UnaryOp):
            op = node.op
            if isinstance(op, ast.USub):
                return -self.eval(node.operand)   # Evaluate the operand and return its negation  (return -x)
            elif isinstance(op, ast.UAdd):
                return +self.eval(node.operand) 
            elif isinstance(op, ast.Not):
                return not self.eval(node.operand)   # Evaluate the operand and return its logical negation (e.g., if x=True, return False)
            
        # For loops
        elif isinstance(node, ast.For):
            iterable = self.eval(node.iter)
            if iterable is not None:
                for item in iterable:  
                    self.variables[node.target.id] = item   # Assign the current item to the loop variable
                    result = self.eval_body(node.body)
                    if isinstance(result, ast.Break):
                        break  
                    elif isinstance(result, ast.Continue):
                        continue
            return None

        # Attribute access
        elif isinstance(node, ast.Attribute): # getting the obj attributes 
            value = self.eval(node.value)
            if value is None:
                return None
            return getattr(value, node.attr, None)
       
        # While loops
        elif isinstance(node, ast.While): 
            while self.eval(node.test): 
                result = self.eval_body(node.body) 
                if isinstance(result, ast.Break):
                    break
                elif isinstance(result, ast.Continue):
                    continue
            return None
        
        # Break statement
        elif isinstance(node, ast.Break):
            return ast.Break()

        # Continue statement
        elif isinstance(node, ast.Continue):
            return ast.Continue()
        
        return None

    def eval_body(self, body):
        result = None
        for node in body:
            result = self.eval(node)
        return result

    def parse_and_eval(self, code):
        # Parse the code into an AST
        tree = ast.parse(code) 
        # Evaluate the code
        return self.eval_body(tree.body)

    def assign(self, target, value):
        if isinstance(target, ast.Name):
            # Direct assignment to a variable
            self.variables[target.id] = value
        elif isinstance(target, ast.Subscript):
            # Assignment to an element of a list or dictionary
            obj = self.eval(target.value)
            if obj is not None:
                if isinstance(target.slice, ast.Index):
                    index = self.eval(target.slice.value)
                elif isinstance(target.slice, ast.Slice):
                    lower = self.eval(target.slice.lower) if target.slice.lower else None
                    upper = self.eval(target.slice.upper) if target.slice.upper else None
                    step = self.eval(target.slice.step) if target.slice.step else None
                    index = slice(lower, upper, step)
                else:
                    index = self.eval(target.slice)
                try:
                    obj[index] = value
                except (IndexError, KeyError, TypeError):
                    pass  

    def repl(self):
        print("Enter your code. Use a blank line to finish input and execute.")
        print("Type 'exit' on a blank line to quit.")
        while True:
            code_lines = []
            while True:
                line = input('... ' if code_lines else '>>> ')
                if not line:
                    if code_lines:
                        break
                    elif line.lower() == 'exit':
                        return
                code_lines.append(line)
            
            code = '\n'.join(code_lines)
            if code.lower() == 'exit':
                break
            
            try:
                result = self.parse_and_eval(code)
                if result is not None:
                    print(result)
            except Exception as e:
                print(f"Error: {e}")

# Custom arithmetic functions
def add(*args):
    if len(args) == 0:
        return 0
    elif len(args) == 1:
        return args[0]
    else:
        return sum(args)

def subtract(*args):
    if len(args) == 0:
        return 0
    elif len(args) == 1:
        return -args[0]
    else:
        result = args[0]
        for num in args[1:]:
            result -= num
        return result

def multiply(*args):
    if len(args) == 0:
        return 0
    elif len(args) == 1:
        return args[0]
    else:
        result = 1
        for num in args:
            result *= num
        return result


def divide(x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

def remove(self, target):
    if isinstance(target, ast.Subscript):    # Check if the target an element from a list or dictionary
        obj = self.eval(target.value)   # Evaluate and store the object being subscripted
        if isinstance(obj, list):   # If it's a list obj
            # Evaluate the slice (the index)
            index = self.eval(target.slice.value) if isinstance(target.slice, ast.Index) else None
            # Check if the evaluated index is valid 
            if index is not None and 0 <= index < len(obj):
                # Remove the element at the specified index
                obj.pop(index)
        # If the object is a dictionary
        elif isinstance(obj, dict):
            # Evaluate the slice (the key) 
            key = self.eval(target.slice.value) if isinstance(target.slice, ast.Index) else None
            if key is not None and key in obj: # Check if the evaluated key is valid 
                del obj[key] # Remove the key and its value

def square(x):
    if x > 0:
        return x ** 0.5
    raise ValueError("Cannot square negative number")

def replace_char(s, old, new):
    if not isinstance(s, str):
        raise TypeError("First argument must be a string")
    if not isinstance(old, str) or not isinstance(new, str):
        raise TypeError("Both old and new must be strings")
    return s.replace(old, new)

def is_upper(s):
    if isinstance(s, str):
        return s.isupper()
    raise TypeError("isUpper function requires a string input")

def is_lower(s):
    if isinstance(s, str):
        return s.islower()
    raise TypeError("isLower function requires a string input")

interpreter = Interpreter()
interpreter.variables.update({
    'print': print,
    'len': len,
    'str': str,
    'int': int,
    'float': float,
    'list': list,
    'tuple': tuple,
    'dict': dict,
    'bool': bool,
    'range': range,
    'sum': sum,
    'min': min,
    'max': max,
    'math': math,
    'add': add,          
    'sub': subtract, 
    'mul': multiply, 
    'div': divide,
    'pow': pow,
    'sqrt': square,
    'replace_char': replace_char,
    'remove': remove,
    'isUpper': is_upper,           
    'isLower': is_lower   
})

example_code = """
# Basic arithmetic and variable assignment
x = 10
y = 5
z = x + y * 2

# Comparison and conditional statements
if z > 20:
    print("z is greater than 20")
else:
    print("z is not greater than 20")

# Lists and list operations
numbers = [1, 2, 3, 4, 5]
squares = []
for num in numbers:
    squares.append(num ** 2)
print("Squares:", squares)

# Dictionary
person = {"name": "Alice", "age": 30}
print("Person:", person)

# String operations
greeting = "Hello, " + person["name"] + "!"
print(greeting)

# Built-in functions
print("Length of squares:", len(squares))
print("Sum of squares:", sum(squares))

# Math operations
radius = 5
area = math.pi * radius ** 2
print("Circle area:", area)

# Slicing
print("First three squares:", squares[:3])

# Boolean operations
is_adult = person["age"] >= 18 and person["name"] != ""
print("Is adult:", is_adult)

# Tuple
coordinates = (10, 20)
print("Coordinates:", coordinates)

# Advanced math
print("Square root of 16:", math.sqrt(16))

# Handling potential None values
empty_list = []
print("First element of empty list:", empty_list[0] if empty_list else None)

# Attribute access on None
none_value = None
print("Attribute of None:", none_value.some_attribute if none_value is not None else None)

# Basic list operations
numbers = [1, 2, 3, 4, 5]

# Remove an item from the list
REMOVE numbers[2]

print(numbers)

original_string = "hello world"
new_string = replace_char(original_string, "l", "x")
print(new_string)  # Output: hexxo worxd

text = "Hello World"
print("Is 'Hello' uppercase?", isUpper("Hello"))
print("Is 'hello' lowercase?", isLower("hello"))
print("Is 'HELLO' uppercase?", isUpper("HELLO"))
print("Is 'WORLD' lowercase?", isLower("WORLD"))
"""
if __name__ == "__main__":
    print("Entering REPL mode:")
    interpreter.repl()

