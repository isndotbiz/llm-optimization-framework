#!/usr/bin/env python3
"""
Condition Evaluator - Safe evaluation of complex workflow conditions
Supports operators: >, <, >=, <=, ==, !=, and, or, not, in, contains
Safely evaluates conditions without code injection risks
"""

from typing import Dict, Any, Tuple
import re


class ConditionEvaluator:
    """Safely evaluate complex workflow conditions"""

    # Supported operators in order of precedence (higher index = lower precedence)
    OPERATORS = {
        'or': {'precedence': 1, 'binary': True},
        'and': {'precedence': 2, 'binary': True},
        'not': {'precedence': 3, 'unary': True},
        '>=': {'precedence': 4, 'binary': True},
        '<=': {'precedence': 4, 'binary': True},
        '>': {'precedence': 4, 'binary': True},
        '<': {'precedence': 4, 'binary': True},
        '!=': {'precedence': 4, 'binary': True},
        '==': {'precedence': 4, 'binary': True},
        'in': {'precedence': 4, 'binary': True},
        'contains': {'precedence': 4, 'binary': True},
    }

    @staticmethod
    def evaluate(condition: str, variables: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluate a condition expression with variable substitution

        Args:
            condition: Condition string (e.g., "(score > 5) and (status == 'active')")
            variables: Dictionary of variables for substitution

        Returns:
            (result, explanation) where result is bool and explanation is str

        Supported syntax:
            - (score > 5) and (status == 'active')
            - name in approved_users
            - description contains 'error'
            - not (is_error)
            - (age >= 18) or (has_permission)
        """
        try:
            # Substitute variables
            substituted = ConditionEvaluator._substitute_variables(condition, variables)

            # Parse and evaluate
            result = ConditionEvaluator._evaluate_expression(substituted)

            return result, f"Condition evaluated to {result}"

        except Exception as e:
            return False, f"Error evaluating condition: {e}"

    @staticmethod
    def _substitute_variables(condition: str, variables: Dict[str, Any]) -> str:
        """
        Replace {{variable}} and bare variable names with their values

        Examples:
            "{{score}} > 5" -> "10 > 5" (if score=10)
            "status == '{{status_var}}'" -> "status == 'active'" (if status_var='active')
        """
        result = condition

        # First substitute {{var}} style
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            # Convert value appropriately
            if isinstance(var_value, str):
                # Check if already quoted
                escaped_value = var_value.replace("'", "\\'")
                result = result.replace(placeholder, f"'{escaped_value}'")
            elif isinstance(var_value, bool):
                result = result.replace(placeholder, str(var_value).lower())
            elif var_value is None:
                result = result.replace(placeholder, "None")
            else:
                result = result.replace(placeholder, str(var_value))

        # Also support unquoted variable names (simplified)
        # Match word boundaries followed by comparison operators
        for var_name in variables.keys():
            # Only substitute if it looks like a variable reference
            if re.search(rf'\b{var_name}\b\s*[><=!]', result):
                var_value = variables[var_name]
                if isinstance(var_value, str):
                    escaped_value = var_value.replace("'", "\\'")
                    result = re.sub(
                        rf'\b{var_name}\b',
                        f"'{escaped_value}'",
                        result,
                        count=1
                    )
                elif isinstance(var_value, bool):
                    result = re.sub(
                        rf'\b{var_name}\b',
                        str(var_value).lower(),
                        result,
                        count=1
                    )
                elif var_value is None:
                    result = re.sub(rf'\b{var_name}\b', "None", result, count=1)
                else:
                    result = re.sub(rf'\b{var_name}\b', str(var_value), result, count=1)

        return result

    @staticmethod
    def _evaluate_expression(expr: str) -> bool:
        """
        Evaluate a substituted expression

        Supports operators with proper precedence:
            - or (lowest precedence)
            - and
            - not
            - comparison operators: >, <, >=, <=, ==, !=, in, contains
        """
        expr = expr.strip()

        # Handle parentheses first
        while '(' in expr:
            # Find innermost parentheses
            match = re.search(r'\(([^()]+)\)', expr)
            if match:
                inner_expr = match.group(1)
                inner_result = ConditionEvaluator._evaluate_expression(inner_expr)
                # Replace with result (as lowercase boolean string)
                expr = expr[:match.start()] + str(inner_result).lower() + expr[match.end():]
            else:
                break

        # Handle 'or' operator (lowest precedence)
        if ' or ' in expr:
            parts = expr.split(' or ')
            for part in parts:
                if ConditionEvaluator._evaluate_expression(part.strip()):
                    return True
            return False

        # Handle 'and' operator
        if ' and ' in expr:
            parts = expr.split(' and ')
            for part in parts:
                if not ConditionEvaluator._evaluate_expression(part.strip()):
                    return False
            return True

        # Handle 'not' operator
        if expr.startswith('not '):
            return not ConditionEvaluator._evaluate_expression(expr[4:].strip())

        # Handle comparison operators
        for op in ['>=', '<=', '!=', '==', '>', '<']:
            if f' {op} ' in expr:
                return ConditionEvaluator._evaluate_comparison(expr, op)

        # Handle 'in' operator
        if ' in ' in expr:
            return ConditionEvaluator._evaluate_in_operator(expr)

        # Handle 'contains' operator
        if ' contains ' in expr:
            return ConditionEvaluator._evaluate_contains_operator(expr)

        # Handle boolean literals
        if expr.lower() == 'true':
            return True
        elif expr.lower() == 'false':
            return False

        raise ValueError(f"Cannot evaluate expression: {expr}")

    @staticmethod
    def _evaluate_comparison(expr: str, operator: str) -> bool:
        """Evaluate comparison operators: >, <, >=, <=, ==, !="""
        parts = expr.split(f' {operator} ', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid comparison: {expr}")

        left = ConditionEvaluator._parse_value(parts[0].strip())
        right = ConditionEvaluator._parse_value(parts[1].strip())

        if operator == '>':
            return left > right
        elif operator == '<':
            return left < right
        elif operator == '>=':
            return left >= right
        elif operator == '<=':
            return left <= right
        elif operator == '==':
            return left == right
        elif operator == '!=':
            return left != right

        return False

    @staticmethod
    def _evaluate_in_operator(expr: str) -> bool:
        """Evaluate 'in' operator for membership testing"""
        parts = expr.split(' in ', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid 'in' expression: {expr}")

        value = ConditionEvaluator._parse_value(parts[0].strip())
        container_expr = parts[1].strip()

        # Container could be a list variable name
        try:
            container = ConditionEvaluator._parse_value(container_expr)
        except:
            # Try to interpret as variable name
            raise ValueError(f"Cannot evaluate container: {container_expr}")

        if isinstance(container, (list, tuple, str)):
            return value in container
        else:
            raise ValueError(f"'in' operator requires list/tuple/string, got {type(container).__name__}")

    @staticmethod
    def _evaluate_contains_operator(expr: str) -> bool:
        """Evaluate 'contains' operator for substring checking"""
        parts = expr.split(' contains ', 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid 'contains' expression: {expr}")

        container = ConditionEvaluator._parse_value(parts[0].strip())
        substring = ConditionEvaluator._parse_value(parts[1].strip())

        if isinstance(container, str) and isinstance(substring, str):
            return substring in container
        else:
            raise ValueError(f"'contains' requires strings, got {type(container).__name__} and {type(substring).__name__}")

    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """
        Parse a value string into appropriate Python type

        Handles:
            - 'string' or "string" -> str
            - 123 -> int
            - 45.6 -> float
            - true/false -> bool
            - [1, 2, 3] -> list
            - None -> None
        """
        value_str = value_str.strip()

        # String literals
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            # Remove quotes and unescape
            return value_str[1:-1].replace("\\'", "'").replace('\\"', '"')

        # Boolean literals
        if value_str.lower() == 'true':
            return True
        elif value_str.lower() == 'false':
            return False

        # None
        if value_str.lower() == 'none':
            return None

        # List literal
        if value_str.startswith('[') and value_str.endswith(']'):
            try:
                # Simple list parsing
                items_str = value_str[1:-1]
                items = [ConditionEvaluator._parse_value(i.strip()) for i in items_str.split(',') if i.strip()]
                return items
            except:
                raise ValueError(f"Cannot parse list: {value_str}")

        # Numeric
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            # Not a number, might be a variable name that wasn't substituted
            raise ValueError(f"Unknown value or unsubstituted variable: {value_str}")

    @staticmethod
    def validate_condition(condition: str) -> Tuple[bool, str]:
        """
        Validate condition syntax without evaluating

        Args:
            condition: Condition string to validate

        Returns:
            (is_valid, message)
        """
        try:
            # Check for balanced parentheses
            open_count = condition.count('(')
            close_count = condition.count(')')
            if open_count != close_count:
                return False, f"Unbalanced parentheses: {open_count} open, {close_count} close"

            # Check for valid operators
            valid_keywords = list(ConditionEvaluator.OPERATORS.keys())
            for keyword in valid_keywords:
                if f' {keyword} ' in condition or condition.startswith(f'{keyword} '):
                    continue

            return True, "Condition syntax is valid"

        except Exception as e:
            return False, f"Invalid condition syntax: {e}"
