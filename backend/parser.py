from enum import Enum
from typing import List, Tuple, Optional, Any
from .schemas import NodeBase
import re

class NodeType(str, Enum):
    OPERATOR = "operator"
    COMPARISON = "comparison"

class Operator(str, Enum):
    AND = "AND"
    OR = "OR"
    GT = ">"
    LT = "<"
    EQ = "="
    GTE = ">="
    LTE = "<="
    
class RuleParser:
    def __init__(self):
        self.operators = {op.value for op in Operator}
        
    def tokenize(self, rule_string: str) -> List[str]:
        # Replace parentheses with spaces around them
        for char in '()':
            rule_string = rule_string.replace(char, f' {char} ')
            
        # Handle string literals properly
        tokens = []
        current_token = ''
        in_string = False
        
        for char in rule_string:
            if char == "'":
                in_string = not in_string
                current_token += char
            elif char.isspace() and not in_string:
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
            else:
                current_token += char
                
        if current_token:
            tokens.append(current_token)
            
        return tokens
    
    def parse_comparison(self, tokens: List[str], index: int) -> Tuple[NodeBase, int]:
        field = tokens[index]
        operator = tokens[index + 1]
        value = tokens[index + 2]
        
        # Handle string literals
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]  # Remove quotes
        else:
            # Try to convert to number
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        
        return NodeBase(
            type=NodeType.COMPARISON,
            operator=operator,
            field=field,
            value=value
        ), index + 3
    
    def parse_expression(self, tokens: List[str], index: int = 0) -> Tuple[NodeBase, int]:
        if tokens[index] == '(':
            left_node, index = self.parse_expression(tokens, index + 1)
            
            if index >= len(tokens):
                raise ValueError("Unexpected end of expression")
            
            operator = tokens[index]
            if operator not in self.operators:
                raise ValueError(f"Invalid operator: {operator}")
            
            index += 1
            right_node, index = self.parse_expression(tokens, index)
            
            if index >= len(tokens) or tokens[index] != ')':
                raise ValueError("Missing closing parenthesis")
            
            return NodeBase(
                type=NodeType.OPERATOR,
                operator=operator,
                left=left_node,
                right=right_node
            ), index + 1
        else:
            return self.parse_comparison(tokens, index)
    
    def create_rule(self, rule_string: str) -> NodeBase:
        tokens = self.tokenize(rule_string)
        node, index = self.parse_expression(tokens)
        
        if index < len(tokens):
            raise ValueError("Unexpected tokens after expression")
            
        return node