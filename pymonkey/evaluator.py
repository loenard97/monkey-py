from typing import List

from pymonkey.ast import BlockStatement, BooleanExpression, CallExpression, Expression, ExpressionStatement, FunctionExpression, Identifier, IfExpression, InfixExpression, IntegerExpression, LetStatement, Node, PrefixExpression, Program, ReturnStatement
from pymonkey.object import IObject, ErrorObject, IntegerObject, BooleanObject, Environment, ReturnValueObject, NullObject, FunctionObject, ValuedObject


def eval(node: Node, env: Environment) -> IObject:
    if isinstance(node, Program):
        return eval_program(node, env)

    # Statement
    elif isinstance(node, BlockStatement):
        return eval_block_statement(node, env)

    elif isinstance(node, ExpressionStatement):
        return eval(node.expression, env)

    elif isinstance(node, ReturnStatement):
        val = eval(node.value, env)
        if isinstance(val, ErrorObject):
            return val
        if isinstance(val, ReturnValueObject):
            return val.value
        return ErrorObject("no return value")

    elif isinstance(node, LetStatement):
        val = eval(node.value, env)
        if isinstance(val, ErrorObject):
            return val
        env.set(node.name.value, val)

    # Expression
    elif isinstance(node, IntegerExpression):
        return IntegerObject(node.value)

    elif isinstance(node, BooleanExpression):
        return BooleanObject(node.value)

    elif isinstance(node, PrefixExpression):
        right = eval(node.right, env)
        if isinstance(right, ErrorObject):
            return right
        return eval_prefix_expression(node.operator, right)

    elif isinstance(node, InfixExpression):
        left = eval(node.left, env)
        if isinstance(left, ErrorObject):
            return left

        right = eval(node.right, env)
        if isinstance(right, ErrorObject):
            return right

        return eval_infix_expression(node.operator, left, right)

    elif isinstance(node, IfExpression):
        return eval_if_expression(node, env)

    elif isinstance(node, Identifier):
        return eval_identifier(node, env)

    elif isinstance(node, FunctionExpression):
        return FunctionObject(node.parameters, node.body, env)

    elif isinstance(node, CallExpression):
        function = eval(node.function, env)
        if isinstance(function, ErrorObject):
            return function

        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and isinstance(args[0], ErrorObject):
            return args[0]
        
        if isinstance(function, FunctionObject):
            return apply_function(function, args)

        return ErrorObject("not a function")

    return NullObject()


def eval_program(program: Program, env: Environment) -> IObject:
    result = NullObject()

    for stmt in program.statements:
        result = eval(stmt, env)

        if isinstance(result, ReturnValueObject):
            return result.value

        if isinstance(result, ErrorObject):
            return result

    return result


def eval_block_statement(block: BlockStatement, env: Environment) -> IObject:
    result = NullObject()

    for stmt in block.statements:
        result = eval(stmt, env)

        if isinstance(result, ReturnValueObject) or isinstance(result, ErrorObject):
            return result

    return result


def native_bool_to_boolean_object(input: bool) -> BooleanObject:
    if input:
        return BooleanObject(True)
    return BooleanObject(False)


def eval_prefix_expression(operator: str, right: IObject) -> IObject:
    match operator:
        case "!":
            return eval_bang_operator_expression(right)
        
        case "-":
            return eval_minus_operator_expression(right)

        case _:
            return ErrorObject("unknown operator")


def eval_infix_expression(operator: str, left: IObject, right: IObject) -> IObject:
    match operator, left.type, right.type:
        case _, "INTEGER_OBJ", "INTEGER_OBJ":
            return eval_integer_infix_expression(operator, left, right)

        case "==", _, _:
            return BooleanObject(left == right)

        case "!=", _, _:
            return BooleanObject(left != right)

    if left.type != right.type:
        return ErrorObject("type mismatch")

    return ErrorObject("unknown operator")


def eval_bang_operator_expression(right: IObject) -> IObject:
    if isinstance(right, BooleanObject):
        return BooleanObject(not right.value)
    return BooleanObject(False)


def eval_minus_operator_expression(right: IObject) -> IObject:
    if isinstance(right, IntegerObject):
        return IntegerObject(-right.value)
    return ErrorObject("unknown operator")


def eval_integer_infix_expression(operator: str, left: IObject, right: IObject) -> IObject:
    if isinstance(left, ValuedObject) and isinstance(right, ValuedObject):
        if operator == "+":
            return IntegerObject(left.value + right.value)

        if operator == "-":
            return IntegerObject(left.value - right.value)

        if operator == "*":
            return IntegerObject(left.value * right.value)

        if operator == "/":
            return IntegerObject(left.value // right.value)

        if operator == "<":
            return BooleanObject(left.value < right.value)

        if operator == ">":
            return BooleanObject(left.value > right.value)

        if operator == "==":
            return BooleanObject(left.value == right.value)

        if operator == "!=":
            return BooleanObject(left.value != right.value)

    return ErrorObject("unknown operator")


def eval_if_expression(ie: IfExpression, env: Environment) -> IObject:
    condition = eval(ie.condition, env)
    if isinstance(condition, ErrorObject):
        return condition

    if is_truthy(condition):
        return eval(ie.consequence, env)

    elif ie.alternative is not None:
        return eval(ie.alternative, env)

    else:
        return NullObject()


def eval_identifier(node: Identifier, env: Environment) -> IObject:
    try:
        val = env.get(node.value)
    except KeyError:
        return ErrorObject("identifier not found")
    else:
        return val


def is_truthy(obj: IObject) -> bool:
    if isinstance(obj, NullObject):
        return False

    if isinstance(obj, BooleanObject):
        return obj.value

    return True


def eval_expressions(exps: List[Expression], env: Environment) -> List[IObject]:
    result = []
    
    for e in exps:
        evaluated = eval(e, env)
        if isinstance(evaluated, ErrorObject):
            return [evaluated]

        result.append(evaluated)

    return result


def apply_function(fn: FunctionObject, args: List[IObject]) -> IObject:
    if fn is None:
        return ErrorObject("not a function")

    extended_env = extend_function_env(fn, args)
    evaluated = eval(fn.body, extended_env)

    if isinstance(evaluated, ReturnValueObject):
        return evaluated.value
    return evaluated


def extend_function_env(fn: FunctionObject, args: List[IObject]) -> Environment:
    env = Environment.new_enclosed(fn.env)

    for i, param in enumerate(fn.parameters):
        env.set(param.value, args[i])

    return env

