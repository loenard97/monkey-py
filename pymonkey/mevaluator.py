from typing import List

from pymonkey.mast import MBlockStatement, MBooleanExpression, MCallExpression, MExpression, MExpressionStatement, MFunctionExpression, MIdentifier, MIfExpression, MInfixExpression, MIntegerExpression, MLetStatement, MNode, MPrefixExpression, MProgram, MReturnStatement
from pymonkey.mobject import MObject, MErrorObject, MIntegerObject, MBooleanObject, MEnvironment, MReturnValueObject, MNullObject, MFunctionObject, MValuedObject


def eval(node: MNode, env: MEnvironment) -> MObject:
    if isinstance(node, MProgram):
        return eval_program(node, env)

    # Statement
    elif isinstance(node, MBlockStatement):
        return eval_block_statement(node, env)

    elif isinstance(node, MExpressionStatement):
        return eval(node.expression, env)

    elif isinstance(node, MReturnStatement):
        print("eval return")
        val = eval(node.value, env)
        print(f"{val=}")
        if isinstance(val, MErrorObject):
            return val
        return MReturnValueObject(val)

    elif isinstance(node, MLetStatement):
        val = eval(node.value, env)
        if isinstance(val, MErrorObject):
            return val
        env.set(node.name.value, val)

    # Expression
    elif isinstance(node, MIntegerExpression):
        return MIntegerObject(node.value)

    elif isinstance(node, MBooleanExpression):
        return MBooleanObject(node.value)

    elif isinstance(node, MPrefixExpression):
        right = eval(node.right, env)
        if isinstance(right, MErrorObject):
            return right
        return eval_prefix_expression(node.operator, right)

    elif isinstance(node, MInfixExpression):
        left = eval(node.left, env)
        if isinstance(left, MErrorObject):
            return left

        right = eval(node.right, env)
        if isinstance(right, MErrorObject):
            return right

        return eval_infix_expression(node.operator, left, right)

    elif isinstance(node, MIfExpression):
        return eval_if_expression(node, env)

    elif isinstance(node, MIdentifier):
        return eval_identifier(node, env)

    elif isinstance(node, MFunctionExpression):
        return MFunctionObject(node.parameters, node.body, env)

    elif isinstance(node, MCallExpression):
        function = eval(node.function, env)
        if isinstance(function, MErrorObject):
            return function

        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and isinstance(args[0], MErrorObject):
            return args[0]
        
        if isinstance(function, MFunctionObject):
            return apply_function(function, args)

        return MErrorObject("not a function")

    return MNullObject()


def eval_program(program: MProgram, env: MEnvironment) -> MObject:
    result = MNullObject()

    for stmt in program.statements:
        result = eval(stmt, env)

        if isinstance(result, MReturnValueObject):
            return result.value

        if isinstance(result, MErrorObject):
            return result

    return result


def eval_block_statement(block: MBlockStatement, env: MEnvironment) -> MObject:
    result = MNullObject()

    for stmt in block.statements:
        result = eval(stmt, env)

        if isinstance(result, MReturnValueObject) or isinstance(result, MErrorObject):
            return result

    return result


def native_bool_to_boolean_object(input: bool) -> MBooleanObject:
    if input:
        return MBooleanObject(True)
    return MBooleanObject(False)


def eval_prefix_expression(operator: str, right: MObject) -> MObject:
    match operator:
        case "!":
            return eval_bang_operator_expression(right)
        
        case "-":
            return eval_minus_operator_expression(right)

        case _:
            return MErrorObject("unknown operator")


def eval_infix_expression(operator: str, left: MObject, right: MObject) -> MObject:
    if isinstance(left, MIntegerObject) and isinstance(right, MIntegerObject):
        return eval_integer_infix_expression(operator, left, right)

    if operator == "==":
        return MBooleanObject(left == right)

    if operator == "!=":
        return MBooleanObject(left != right)

    if type(left) != type(right):
        return MErrorObject(f"type mismatch in {type(left)} {operator} {type(right)}")

    return MErrorObject("unknown operator {type(left)} {operator} {type(right)}")


def eval_bang_operator_expression(right: MObject) -> MObject:
    if isinstance(right, MBooleanObject):
        return MBooleanObject(not right.value)
    return MBooleanObject(False)


def eval_minus_operator_expression(right: MObject) -> MObject:
    if isinstance(right, MIntegerObject):
        return MIntegerObject(-right.value)
    return MErrorObject("unknown operator")


def eval_integer_infix_expression(operator: str, left: MObject, right: MObject) -> MObject:
    if isinstance(left, MValuedObject) and isinstance(right, MValuedObject):
        if operator == "+":
            return MIntegerObject(left.value + right.value)

        if operator == "-":
            return MIntegerObject(left.value - right.value)

        if operator == "*":
            return MIntegerObject(left.value * right.value)

        if operator == "/":
            return MIntegerObject(left.value // right.value)

        if operator == "<":
            return MBooleanObject(left.value < right.value)

        if operator == ">":
            return MBooleanObject(left.value > right.value)

        if operator == "==":
            return MBooleanObject(left.value == right.value)

        if operator == "!=":
            return MBooleanObject(left.value != right.value)

    return MErrorObject("unknown operator")


def eval_if_expression(ie: MIfExpression, env: MEnvironment) -> MObject:
    condition = eval(ie.condition, env)
    if isinstance(condition, MErrorObject):
        return condition

    if is_truthy(condition):
        return eval(ie.consequence, env)

    elif ie.alternative is not None:
        return eval(ie.alternative, env)

    else:
        return MNullObject()


def eval_identifier(node: MIdentifier, env: MEnvironment) -> MObject:
    try:
        val = env.get(node.value)
    except KeyError:
        return MErrorObject("identifier not found")
    else:
        return val


def is_truthy(obj: MObject) -> bool:
    if isinstance(obj, MNullObject):
        return False

    if isinstance(obj, MBooleanObject):
        return obj.value

    return True


def eval_expressions(exps: List[MExpression], env: MEnvironment) -> List[MObject]:
    result = []
    
    for e in exps:
        evaluated = eval(e, env)
        if isinstance(evaluated, MErrorObject):
            return [evaluated]

        result.append(evaluated)

    return result


def apply_function(fn: MFunctionObject, args: List[MObject]) -> MObject:
    if fn is None:
        return MErrorObject("not a function")

    extended_env = extend_function_env(fn, args)
    evaluated = eval(fn.body, extended_env)

    if isinstance(evaluated, MReturnValueObject):
        return evaluated.value
    return evaluated


def extend_function_env(fn: MFunctionObject, args: List[MObject]) -> MEnvironment:
    env = MEnvironment.new_enclosed(fn.env)

    for i, param in enumerate(fn.parameters):
        env.set(param.value, args[i])

    return env

