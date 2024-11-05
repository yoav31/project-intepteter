#Name: Idan Alashvili , ID:326117629
#Name: Maor Pinhas , ID:324170885
#Name: Yoav Vaknin , ID:208323261
#Name: Matan Mezamer Tov, ID:208414516

import math
import ast

class Interpreter:

    #פונקציית בנאי של האינטרפטר
    def __init__(self):
        #מילון ריק שמכיל את כל המשתנים הנוצרים במהלך ריצת האינטרפטר
        self.variables = {}
        #מילון שבו כל סוג של פעולה מתאימה לפונקציית למבדה שמבצעת אותה
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

#הפונקציה טוקנייז: מפרקת את הקוד לעץ תחבירי ומייצרת רשימת טוקנים לכל המרכיבים של הקוד (כמו קבועים, אופרטורים השוואות השמות וכו)
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

# זוהי הפונקציה העיקרית במפרש היא מעריכה את ערכי הצמתים השונים של העץ התחבירי ומבצעת את החישובים הנדרשים  
#למשל: 
#קבועים: אם הצומת הוא קבוע (כמו מספר), הפונקציה מחזירה את הערך שלו
#שמות משתנים: אם הצומת הוא משתנה הפונקציה תחזיר את הערך שלו מהמילון
#אופרטורים בינאריים: אם הצומת הוא אופרטור בינארי (כמו +,-) הפונקציה מעריכה את שני האופרנדים ומבצעת את הפעולה המתאימה באמצעות טבלת ה-דיספאטץ
    def eval(self, node):
        # Constants
        if isinstance(node, ast.Constant):
            return node.value
        
        # Variables Name
        elif isinstance(node, ast.Name):
            return self.variables.get(node.id)
        
        # Binary Operations
        elif isinstance(node, ast.BinOp):
            left = self.eval(node.left)
            right = self.eval(node.right)
            if left is None or right is None:
                return None
            return self.dispatch[type(node.op)](left, right)
        
        # Comparison
        #הערכה של השוואות: מטפלת באופרטורים של השוואה כמו >, < וכו. היא משווה בין הערך משמאל למשתנים משמאל.
        elif isinstance(node, ast.Compare):
            #שורה זו מחשבת את הערך של האיבר השמאלי בהשוואה
            #למשל עבור א<ב אז האיבר השמאלי יהיה ב
            left = self.eval(node.left)

            #לולאה שעוברת על כל האופרטורים והאיברים המושווים: מכיוון שיכולות להיות מספר השוואות יחד שורה זו מבצעת לולאה על כל האופרטורים (כמו גדול, קטן שווה וכו) והאיברים המושווים על ידי שימוש בפונקציה זיפ שמשלבת את שתי הרשימות האלו יחד ללולאה אחת.
            for op, right in zip(node.ops, node.comparators):
                #שורה זו מחשבת את הערך של האיבר הימני בהשוואה הנוכחית
                right_val = self.eval(right)
                #כאן הקוד מבצע את ההשוואה בפועל. 
                if not self.dispatch[type(op)](left, right_val):
                    return False
                left = right_val
            return True
        
        # Logical Operations
        #פעולות לוגיות: מטפלת בפעולות לוגיות כמו "וגם" ו-"או". בפעולת וגם כל הערכים צריכים להיות אמת וב-או לפחות אחד צריך להיות אמת 
        elif isinstance(node, ast.BoolOp):
            values = [self.eval(value) for value in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            elif isinstance(node.op, ast.Or):
                return any(values)
        
        # Assignment
        #השמה (=): הפעולה מעריכה את הערך בצד ימין ומשבצת אותו במשתנים בצד שמאל 
        elif isinstance(node, ast.Assign):
            value = self.eval(node.value)
            for target in node.targets:
                self.assign(target, value)
            return value
        
        # If-statements
        #פקודות "אם": מעריכה את התנאי בפקודת ה-"אם" אם התנאי מתקיים מבצעים את גוף הקוד שבתוך התנאי אחרת מדלגים על גוף הקוד ועוברים לקטע הקוד שאחריו
        elif isinstance(node, ast.If):
            if self.eval(node.test):
                return self.eval_body(node.body)
            elif node.orelse:
                return self.eval_body(node.orelse)
        
        # Expressions
        #ביטויים: מעריכה ביטויים בודדים כמו קריאות לפונקציות או פעולות אריתמטיות.
        elif isinstance(node, ast.Expr):
            return self.eval(node.value)
        
        # Callables
        elif isinstance(node, ast.Call):
            func = self.eval(node.func)
            args = [self.eval(arg) for arg in node.args]
            return func(*args)
        
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
        #בדיקה האם הצומת הוא תת מפתח, כלומר גישה לאיבר ברשימה,מילון או מערך כלשהו באמצעות אינדקס
        elif isinstance(node, ast.Subscript):
            #שורה זו מעריכה את הערך של הצומת בעץ שנמצא לפני הסוגריים המרובעים כלומר הערך של מערך מספרים מסויים יהיה כל המערך
            value = self.eval(node.value) 
            #אם הערך הוא ריק אז מחזירים ריק
            if value is None:
                return None
            #אם הצומת מייצגת גישה לפי אינדקס יחיד אז השורה שבתנאי מעריכה את האינדקס 
            if isinstance(node.slice, ast.Index):   
                index = self.eval(node.slice.value)
            #אם במקום אינדקס יחיד יש חיתןך של מספר איברים למשל אינדקס 1 עד 4 במערך השורה אינדקס שבתנאי נכנסת להערכת החיתוך    
            elif isinstance(node.slice, ast.Slice):
                lower = self.eval(node.slice.lower) if node.slice.lower else None
                upper = self.eval(node.slice.upper) if node.slice.upper else None
                step = self.eval(node.slice.step) if node.slice.step else None
                index = slice(lower, upper, step)

                #מקרה אחר: אם זה לא אינדקס ולא חיתוך (מקרה נדיר) הקוד מעריך את הפרוסה באופציה אחרת
            else:
                index = self.eval(node.slice)

                #בשורה זו מנסים לגשת לאיבר ברצף מסוג מסוים לפי האינדקס או החיתוך שלו.
                #אם יש שגיאות כמו אינדקס מחוץ לטווח וכו הקוד יחזיר כלום במקום לזרוק שגיאה.
            try:
                return value[index]
            except (IndexError, KeyError, TypeError):
                return None
        

        # Slice
        #בדיקה אם הצומת הוא חיתוך: הם הצומת מייצגת פעולה של חיתוך (כלומר גישה לטווח של ערכים)
        elif isinstance(node, ast.Slice):
            #הערכת הגבולות של החיתוך: שורות אלו מעריכות את הגבולות התחתונים והעליונים של החיתוך ואת צעד הקפיצה שלו.
            #אם גבול כלשהו אינו קיים, הערך שלו יהיה ריק
            lower = self.eval(node.lower) if node.lower else None
            upper = self.eval(node.upper) if node.upper else None
            step = self.eval(node.step) if node.step else None
            return slice(lower, upper, step)
        
        # Unary Ops
        #שורה זו בודקת אם הצומת היא פעולה אונארית, כלומר פעולה שפועלת על ערך יחיד (כמו סימן שלילי או שלילה לוגית)
        elif isinstance(node, ast.UnaryOp):
            op = node.op
            #סימן שלילי: בדיקה האם האופרטור הוא סימן שלילי
            #אם כן השורה שבתנאי תגרום לפונקציה להחזיר את הערך הנגדי של האופרנד
            if isinstance(op, ast.USub):
                return -self.eval(node.operand)
            #סימן חיובי: בדיקה  האם האופרטור הוא סימן חיובי
            #אם כן השורה שבתנאי תגרום לפונקציה להחזיר את הערך של האופרנד כמו שהוא
            elif isinstance(op, ast.UAdd):
                return +self.eval(node.operand)
            #שלילה לוגית: אם האופרטור הוא שלילה לוגית השורה שבתנאי תגרום לפונקציה להחזיר את הערך ההפוך מבחינה לוגית של האופרנד (אמת יהפוך לשקר וההפך)
            elif isinstance(op, ast.Not):
                return not self.eval(node.operand)
        
        # For loops
        elif isinstance(node, ast.For):
            iterable = self.eval(node.iter)
            if iterable is not None:
                for item in iterable:
                    #כאן משויכת הערך הנוכחי של האיטרציה למשתנה הלולאה (כלומר, מבוצעת הצבה של ערך הנוכחי במשתנה).
                    self.variables[node.target.id] = item
                    #כאן מתבצע הקוד שנמצא בתוך גוף הלולאה
                    result = self.eval_body(node.body)
                    #אם גוף הלולאה מכיל את הפקודה "עצור" נבצע את הפקודה ונצא מהלולאה באמצע ריצתה
                    if isinstance(result, ast.Break):
                        break  
                    #אם גוף הלולאה מכיל את הפקודה "המשך" נבצע את הפקודה ונסיים את האיטרציה הנוכחית
                    elif isinstance(result, ast.Continue):
                        continue
            return None

        # Attribute access
        elif isinstance(node, ast.Attribute):
            #תחילה בודקים את הערך של האובייקט שאליו מתייחסים
            value = self.eval(node.value)
            if value is None:
                return None
            #בשורה זו משתמשים בפונקציה "גטאטרר" של פייתון כדי לקבל את הערך של הארטריביוט של האובייקט. אם האטריביוט לא קיים מחזירים ריק
            return getattr(value, node.attr, None)
        
        # While loops
        elif isinstance(node, ast.While):
            #בשורה זו מבוצעת הערכה של תנאי הלולאה. אם הערך הוא אמת נכנסים לגוף הלולאה
            while self.eval(node.test):
                result = self.eval_body(node.body)
                #בדיקת פקודות "המשך" ו-"שבור" אם הערך של ריזולט מחזיר את הפקודה "שבור" נשבור את הלולאה, אם הוא מחזיר "המשך" נמשיך ישירות לאיטרציה הבאה
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
        
        #calling to a function
        elif isinstance(node, ast.Call):
            #הערכה של הפונקציה (מהי הפונקציה שיש לקרוא לה)
            func = self.eval(node.func)
            #הערכה לכל אחד מהארגומנטים שנמסרו לפונקציה
            args = [self.eval(arg) for arg in node.args]
            #בדיקה האם הפונקציה ניתנת לקריאה
            #אם כן קוראים ומבצעים את הפונקציה יחד עם הארגומנטים שניתנו לה
            if callable(func):
                return func(*args)
            #אם לא תיזרק שגיאה
            else:
                raise TypeError(f"{func} is not callable")

        return None


#הפונקציה אחראית על הערכת ה-"גוף" של הקוד. כלומר מה הקוד עושה לדוגמא קריאה לפונקציה.
#הפונקציה מקבלת כפרמטר את המשתנה בודי שהוא רשימה של פקודות
    def eval_body(self, body):
        result = None    #מאתחל את התוצאה לכלום
        #עבור כל פקודה בבודי אנחנו קוראים לפונקציה איבל כדי להעריך את הפקודה
        for node in body:
            #הפונקציה מחזיקה את התוצאה האחרונה של הפקודה במשתנה תוצאה אשר היא מחזירה אותו בסוף
            result = self.eval(node)
        return result

#פונקציה זו קוראת קוד, מפרקת אותו לעץ התחבירי ומבצעת את הערכתו
    def parse_and_eval(self, code):
        # Parse the code into an AST
        tree = ast.parse(code)
        
        # Evaluate the code
        return self.eval_body(tree.body)


#הפונקציה אחראית על ביצוע השמה של ערכים למשתנים או לרשימות בעזרת אינדקסים או טווחים. 
    def assign(self, target, value):
        #אם המטרה הוא מסוג משתנה רגיל פשוט מקצים את הערך למשתנה במילון המשתנים
        if isinstance(target, ast.Name):
            # Direct assignment to a variable
            #target.id - the name of the variable
            #value- the value of the variable after the assignment
            self.variables[target.id] = value
          #אם המטרה הוא אינדקס במבנה נתונים מסוים כמו מערך, הפונקציה מבצעת השמה לאיבר מסוים במבנה הנתונים  
        elif isinstance(target, ast.Subscript):
            # Assignment to an element of a list or dictionary
            #obj= the value of the data structure where we want to do the assign
            obj = self.eval(target.value)
            if obj is not None:
                #בדיקה אם ההשמה מתבצעת לאינדקס בודד במבנה הנתונים
                if isinstance(target.slice, ast.Index):
                    #אם כן: מוצאים את האינדקס ושומרים אותו במשתנה
                    index = self.eval(target.slice.value)

                    #בדיקה האם ההשמה מתבצעת על טווח של אינדקסים ובקפיצה מסוימת בניהם
                elif isinstance(target.slice, ast.Slice):
                    #אם כן: 
                    #lower- the low index of the range (the start)
                    #upper- the highest index of the range (the end)
                    #step- the jump between the indexes
                    lower = self.eval(target.slice.lower) if target.slice.lower else None
                    upper = self.eval(target.slice.upper) if target.slice.upper else None
                    step = self.eval(target.slice.step) if target.slice.step else None
                    index = slice(lower, upper, step)
                else:
                    index = self.eval(target.slice)
                    #ניסיון ביצוע ההשמה
                try:
                    obj[index] = value
                    #טיפול בשגיאות: כאשר אחת משלושת השגיאות קוראת הפונקציה תפסיק את הנסיון ותמשיך ללא ביצוע ההשמה
                except (IndexError, KeyError, TypeError):
                    pass  

#הפונקציה יוצרת לולאה פשוטה שקוראת קלט מהמשתמש, מעריכה אותו ומדפיסה את התוצאה. הלולאה תמשיך לרוץ עד שהמשתמש יצא.
    def repl(self):
        print("Enter your code. Use a blank line to finish input and execute.")
        print("Type 'exit' on a blank line to quit.")
        #start of the main infinite loop of the repl
        # the loop ends when the user enters 'exit' 
        while True:
            #initialize a list of the code lines from the user
            code_lines = []
            #לולאה פנימית עבור הקטע קוד הנוכחי, נועדה עבור קטע קוד של מספר שורות כמו תנאי ולולאות
            while True:
                #נוצרת למשתמש שורה חדשה לכתיבת קוד
                #אם אנחנו בתוך קטע קוד מסויים תחילת השורה תתחיל : ... אם אנחנו בתחילתו של קטע קוד חדש השורה תתחיל עם >>ע
                line = input('... ' if code_lines else '>>> ')

                #אם המשתמש הכניס שורת קוד ריקה
                if not line:
                    #אם כבר יש שורות בקטע קוד הנל הלולאה הפנימית תסתיים והתוכנית תבצע את הקוד
                    if code_lines:
                        break
                    #אם המשתמש הכניס אקזית הפונקציה תסתיים כך שהמשתמש לא יוכל יותר להכניס שורות קוד
                    elif line.lower() == 'exit':
                        return
                code_lines.append(line)
            # מאחדים את כל השורות שנכתבו בקטע קוד בלולאה הפנימית לשורה אחת גדולה עם הפרדה לפי שורות, בעצם מכינים את הקטע קוד להרצה
            code = '\n'.join(code_lines)
            #אם המשתמש הכניס אקזיט בתוך הקוד הלולאה הראשית תיפסק וככה המשתמש לא יוכל להכניס יותר שורות קוד
            if code.lower() == 'exit':
                break
            
            #מנסים להריץ את הקוד שהמשתמש הכניס
            try:
                #קריאה לפונקציה שמפרשת את הקוד ומעריכה אותו
                result = self.parse_and_eval(code)
                #אם התוצאה היא לא כלום הפלט יודפס למסך
                if result is not None:
                    print(result)
#אם מתרחשת שגיאה כלשהיא במהלך הרצת הקוד השגיאה תיתפס ותודפס כהודעת שגיאה
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
    if isinstance(target, ast.Subscript):
        obj = self.eval(target.value)
        if isinstance(obj, list):
            index = self.eval(target.slice.value) if isinstance(target.slice, ast.Index) else None
            if index is not None and 0 <= index < len(obj):
                obj.pop(index)
        elif isinstance(obj, dict):
            key = self.eval(target.slice.value) if isinstance(target.slice, ast.Index) else None
            if key is not None and key in obj:
                del obj[key]

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

# Add built-in functions and modules
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
