from typing import Dict, Any, List, Set
from enum import Enum
from .schemas import NodeBase
from .parser import Operator, NodeType, NodeBase

class RuleEvaluator:
    def evaluate_comparison(self, node: NodeBase, data: Dict[str, Any]) -> bool:
        field_value = data.get(node.field)
        if field_value is None:
            raise ValueError(f"Field '{node.field}' not found in data")
        
        if node.operator == Operator.GT:
            return field_value > node.value
        elif node.operator == Operator.LT:
            return field_value < node.value
        elif node.operator == Operator.EQ:
            return field_value == node.value
        elif node.operator == Operator.GTE:
            return field_value >= node.value
        elif node.operator == Operator.LTE:
            return field_value <= node.value
        else:
            raise ValueError(f"Invalid comparison operator: {node.operator}")
    
    def evaluate_rule(self, node: NodeBase, data: Dict[str, Any]) -> bool:
        if node.type == NodeType.OPERATOR:
            left_result = self.evaluate_rule(node.left, data)
            right_result = self.evaluate_rule(node.right, data)
            
            if node.operator == Operator.AND:
                return left_result and right_result
            elif node.operator == Operator.OR:
                return left_result or right_result
            else:
                raise ValueError(f"Invalid logical operator: {node.operator}")
                
        elif node.type == NodeType.COMPARISON:
            return self.evaluate_comparison(node, data)
        
        raise ValueError(f"Invalid node type: {node.type}")
    
    def combine_rules(self, rules: List[NodeBase], combine_operator: Operator = Operator.OR) -> NodeBase:

        if not rules:
            raise ValueError("No rules to combine")
            
        if len(rules) == 1:
            return rules[0]
        
        # Flatten nested operations of same type
        flattened_rules = self._flatten_rules(rules, combine_operator)
        
        # Deduplicate identical conditions
        unique_rules = self._deduplicate_rules(flattened_rules)
        
        # Group common conditions
        optimized_rules = self._group_common_conditions(unique_rules, combine_operator)
        
        # If we only have one rule after optimization, return it
        if len(optimized_rules) == 1:
            return optimized_rules[0]
            
        # Create balanced tree instead of linear chain
        return self._create_balanced_tree(optimized_rules, combine_operator)
    
    def _flatten_rules(self, rules: List[NodeBase], operator: Operator) -> List[NodeBase]:
        result = []
        for rule in rules:
            if (rule.type == NodeType.OPERATOR and 
                rule.operator == operator.value):
                # Recursively flatten nested operations
                result.extend(self._flatten_rules([rule.left, rule.right], operator))
            else:
                result.append(rule)
        return result
    
    def _deduplicate_rules(self, rules: List[NodeBase]) -> List[NodeBase]:
        seen = set()
        unique_rules = []
        
        for rule in rules:
            rule_str = self._node_to_string(rule)
            if rule_str not in seen:
                seen.add(rule_str)
                unique_rules.append(rule)
        
        return unique_rules
    
    def _group_common_conditions(self, rules: List[NodeBase], operator: Operator) -> List[NodeBase]:
        condition_map: Dict[str, List[NodeBase]] = {}
        
        # Group rules by common conditions
        for rule in rules:
            conditions = self._extract_conditions(rule)
            key = frozenset(conditions)
            condition_map.setdefault(str(key), []).append(rule)
        
        # Combine rules with common conditions
        optimized_rules = []
        for rules_group in condition_map.values():
            if len(rules_group) > 1:
                # Create optimized subtree for rules with common conditions
                optimized_rules.append(self._create_balanced_tree(rules_group, operator))
            else:
                optimized_rules.extend(rules_group)
        
        return optimized_rules
    
    def _create_balanced_tree(self, rules: List[NodeBase], operator: Operator) -> NodeBase:
        if len(rules) == 1:
            return rules[0]
        if len(rules) == 2:
            return NodeBase(
                type=NodeType.OPERATOR,
                operator=operator.value,
                left=rules[0],
                right=rules[1]
            )
            
        mid = len(rules) // 2
        return NodeBase(
            type=NodeType.OPERATOR,
            operator=operator.value,
            left=self._create_balanced_tree(rules[:mid], operator),
            right=self._create_balanced_tree(rules[mid:], operator)
        )
    
    def _node_to_string(self, node: NodeBase) -> str:
        if node.type == NodeType.OPERATOR:
            return f"({self._node_to_string(node.left)} {node.operator} {self._node_to_string(node.right)})"
        return f"{node.field} {node.operator} {node.value}"
    
    def _extract_conditions(self, node: NodeBase) -> Set[str]:
        conditions = set()
        if node.type == NodeType.OPERATOR:
            conditions.update(self._extract_conditions(node.left))
            conditions.update(self._extract_conditions(node.right))
        else:
            conditions.add(self._node_to_string(node))
        return conditions