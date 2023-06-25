from typing import List

from pymonkey.evaluator.mbuiltins import Builtins
from pymonkey.evaluator.mobject import (
    MArrayObject,
    MBooleanObject,
    MBuiltinFunction,
    MEnvironment,
    MErrorObject,
    MFunctionObject,
    MIntegerObject,
    MNullObject,
    MObject,
    MReturnValueObject,
    MStringObject,
    MValuedObject,
)
from pymonkey.parser.mast import (
    MArrayExpression,
    MBlockStatement,
    MBooleanExpression,
    MCallExpression,
    MExpression,
    MExpressionStatement,
    MFunctionExpression,
    MIdentifier,
    MIfExpression,
    MIndexExpression,
    MInfixExpression,
    MIntegerExpression,
    MLetStatement,
    MNode,
    MPrefixExpression,
    MProgram,
    MReturnStatement,
    MStringExpression,
)
from pymonkey.util import flog


class MEvaluator:
    def __init__(self, top_node: MNode):
        self.top_node = top_node
        self.top_env = MEnvironment()

    @flog
    def evaluate(self):
        return MEvaluator.eval_node(self.top_node, self.top_env)

    @classmethod
    @flog
    def eval_node(cls, node: MNode, env: MEnvironment) -> MObject:
        if isinstance(node, MProgram):
            return MEvaluator.eval_program(node, env)

        # Statement
        elif isinstance(node, MBlockStatement):
            return MEvaluator.eval_block_statement(node, env)

        elif isinstance(node, MExpressionStatement):
            return MEvaluator.eval_node(node.expression, env)

        elif isinstance(node, MReturnStatement):
            val = MEvaluator.eval_node(node.value, env)
            if isinstance(val, MErrorObject):
                return val
            return MReturnValueObject(val)

        elif isinstance(node, MLetStatement):
            val = MEvaluator.eval_node(node.value, env)
            if isinstance(val, MErrorObject):
                return val
            env.set(node.name.value, val)

        # Expression
        elif isinstance(node, MIntegerExpression):
            return MIntegerObject(node.value)

        elif isinstance(node, MBooleanExpression):
            return MBooleanObject(node.value)

        elif isinstance(node, MStringExpression):
            return MStringObject(node.value)

        elif isinstance(node, MArrayExpression):
            elements = MEvaluator.eval_expressions(node.value, env)
            if len(elements) == 1 and isinstance(elements[0], MErrorObject):
                return elements[0]
            return MArrayObject(elements)

        elif isinstance(node, MIndexExpression):
            left = MEvaluator.eval_node(node.left, env)
            if isinstance(left, MErrorObject):
                return left

            index = MEvaluator.eval_node(node.index, env)
            if isinstance(index, MErrorObject):
                return index

            return MEvaluator.eval_index_expression(left, index)

        elif isinstance(node, MPrefixExpression):
            right = MEvaluator.eval_node(node.right, env)
            if isinstance(right, MErrorObject):
                return right
            return MEvaluator.eval_prefix_expression(node.operator, right)

        elif isinstance(node, MInfixExpression):
            left = MEvaluator.eval_node(node.left, env)
            if isinstance(left, MErrorObject):
                return left

            right = MEvaluator.eval_node(node.right, env)
            if isinstance(right, MErrorObject):
                return right

            return MEvaluator.eval_infix_expression(node.operator, left, right)

        elif isinstance(node, MIfExpression):
            ret = MEvaluator.eval_if_expression(node, env)
            print(f"{ret=}")
            return ret

        elif isinstance(node, MIdentifier):
            return MEvaluator.eval_identifier(node, env)

        elif isinstance(node, MFunctionExpression):
            return MFunctionObject(node.parameters, node.body, env)

        elif isinstance(node, MCallExpression):
            function = MEvaluator.eval_node(node.function, env)
            if isinstance(function, MErrorObject):
                return function

            args = MEvaluator.eval_expressions(node.arguments, env)
            if len(args) == 1 and isinstance(args[0], MErrorObject):
                return args[0]

            if isinstance(function, MFunctionObject):
                return MEvaluator.apply_function(function, args)

            if isinstance(function, MBuiltinFunction):
                return MEvaluator.apply_builtin(function, args)

            return MErrorObject("not a function")

        return MNullObject()

    @classmethod
    @flog
    def eval_program(cls, program: MProgram, env: MEnvironment) -> MObject:
        result: MObject = MNullObject()

        for stmt in program.statements:
            result = MEvaluator.eval_node(stmt, env)

            if isinstance(result, MReturnValueObject):
                return result.value

            if isinstance(result, MErrorObject):
                return result

        return result

    @classmethod
    @flog
    def eval_block_statement(cls, block: MBlockStatement, env: MEnvironment) -> MObject:
        result: MObject = MNullObject()

        for stmt in block.statements:
            result = MEvaluator.eval_node(stmt, env)

            if isinstance(result, MReturnValueObject) or isinstance(
                result, MErrorObject
            ):
                return result

        return result

    @classmethod
    @flog
    def native_bool_to_boolean_object(cls, input: bool) -> MBooleanObject:
        if input:
            return MBooleanObject(True)
        return MBooleanObject(False)

    @classmethod
    @flog
    def eval_prefix_expression(cls, operator: str, right: MObject) -> MObject:
        match operator:
            case "!":
                return MEvaluator.eval_bang_operator_expression(right)

            case "-":
                return MEvaluator.eval_minus_operator_expression(right)

            case _:
                return MErrorObject("unknown operator")

    @classmethod
    @flog
    def eval_infix_expression(
        cls, operator: str, left: MObject, right: MObject
    ) -> MObject:
        if isinstance(left, MIntegerObject) and isinstance(right, MIntegerObject):
            return MEvaluator.eval_integer_infix_expression(operator, left, right)

        if isinstance(left, MStringObject) and isinstance(right, MStringObject):
            return MEvaluator.eval_string_infix_expression(operator, left, right)

        if operator == "==":
            return MBooleanObject(left == right)

        if operator == "!=":
            return MBooleanObject(left != right)

        if type(left) != type(right):
            return MErrorObject(
                f"type mismatch in {type(left)} {operator} {type(right)}"
            )

        return MErrorObject("unknown operator {type(left)} {operator} {type(right)}")

    @classmethod
    @flog
    def eval_bang_operator_expression(cls, right: MObject) -> MObject:
        if isinstance(right, MBooleanObject):
            return MBooleanObject(not right.value)
        return MBooleanObject(False)

    @classmethod
    @flog
    def eval_minus_operator_expression(cls, right: MObject) -> MObject:
        if isinstance(right, MIntegerObject):
            return MIntegerObject(-right.value)
        return MErrorObject("unknown operator")

    @classmethod
    @flog
    def eval_integer_infix_expression(
        cls, operator: str, left: MIntegerObject, right: MIntegerObject
    ) -> MObject:
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

    @classmethod
    def eval_string_infix_expression(
        cls, operator: str, left: MStringObject, right: MStringObject
    ) -> MObject:
        if operator == "+":
            return MStringObject(left.value + right.value)

        return MErrorObject("unknown str operator")

    @classmethod
    @flog
    def eval_if_expression(cls, ie: MIfExpression, env: MEnvironment) -> MObject:
        condition = MEvaluator.eval_node(ie.condition, env)
        if isinstance(condition, MErrorObject):
            return condition

        if MEvaluator.is_truthy(condition):
            return MEvaluator.eval_node(ie.consequence, env)

        elif ie.alternative is not None:
            return MEvaluator.eval_node(ie.alternative, env)

        else:
            return MNullObject()

    @classmethod
    @flog
    def eval_identifier(cls, node: MIdentifier, env: MEnvironment) -> MObject:
        try:
            val = env.get(node.value)
        except KeyError:
            pass
            # return MErrorObject("identifier not found")
        else:
            return val

        try:
            print("builtin", node.value)
            val = Builtins().fns[node.value]
        except KeyError:
            return MErrorObject("identifier not found")

        return val

    @classmethod
    @flog
    def is_truthy(cls, obj: MObject) -> bool:
        if isinstance(obj, MNullObject):
            return False

        if isinstance(obj, MBooleanObject):
            return obj.value

        return True

    @classmethod
    @flog
    def eval_expressions(
        cls, exps: List[MExpression], env: MEnvironment
    ) -> List[MObject]:
        result = []

        for e in exps:
            evaluated = MEvaluator.eval_node(e, env)
            if isinstance(evaluated, MErrorObject):
                return [evaluated]

            result.append(evaluated)

        return result

    @classmethod
    def eval_index_expression(cls, left: MObject, index: MObject) -> MObject:
        if isinstance(left, MArrayObject) and isinstance(index, MIntegerObject):
            return MEvaluator.eval_array_index_expression(left, index)

        return MErrorObject("index operator not supported")

    @classmethod
    def eval_array_index_expression(
        cls, left: MArrayObject, index: MIntegerObject
    ) -> MObject:
        max = len(left.value) - 1

        if index.value < 0 or index.value > max:
            return MNullObject()

        return left.value[index.value]

    @classmethod
    @flog
    def apply_function(cls, fn: MFunctionObject, args: List[MObject]) -> MObject:
        extended_env = MEvaluator.extend_function_env(fn, args)
        evaluated = MEvaluator.eval_node(fn.body, extended_env)

        if isinstance(evaluated, MReturnValueObject):
            return evaluated.value
        return evaluated

    @classmethod
    @flog
    def apply_builtin(cls, fn: MBuiltinFunction, args: List[MObject]) -> MObject:
        print("apply bi", args)
        return fn.fn(args)

    @classmethod
    @flog
    def extend_function_env(
        cls, fn: MFunctionObject, args: List[MObject]
    ) -> MEnvironment:
        env = MEnvironment.new_enclosed(fn.env)

        for i, param in enumerate(fn.parameters):
            env.set(param.token.literal, args[i])

        return env
