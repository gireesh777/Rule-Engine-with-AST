from flask import Flask, request, jsonify, render_template
import sqlite3
import json
from dataclasses import dataclass
from typing import Optional, Dict, List

app = Flask(__name__)

# Define the Node structure using dataclass
@dataclass
class Node:
    type: str  # 'operator' or 'operand'
    value: Optional[str] = None
    left: Optional['Node'] = None
    right: Optional['Node'] = None

# Database initialization
def init_db():
    conn = sqlite3.connect('rules.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rule_string TEXT NOT NULL,
            ast_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Helper functions for rule parsing and evaluation (same as before)

# Tokenization function
def tokenize(rule_string: str) -> List[str]:
    operators = ['AND', 'OR', '>', '<', '=', '(', ')']
    tokens = []
    current = ''
    
    i = 0
    while i < len(rule_string):
        if rule_string[i].isspace():
            if current:
                tokens.append(current)
                current = ''
            i += 1
            continue
            
        if rule_string[i:i+3] in ['AND', 'OR']:
            if current:
                tokens.append(current)
                current = ''
            tokens.append(rule_string[i:i+3])
            i += 3
            continue
            
        if rule_string[i] in ['(', ')', '>', '<', '=']:
            if current:
                tokens.append(current)
                current = ''
            tokens.append(rule_string[i])
            i += 1
            continue
            
        current += rule_string[i]
        i += 1
        
    if current:
        tokens.append(current)
        
    return tokens

# AST Parsing function
def parse_expression(tokens: List[str], pos: int = 0) -> tuple[Node, int]:
    if pos >= len(tokens):
        raise ValueError("Unexpected end of expression")
        
    if tokens[pos] == '(':
        left_node, pos = parse_expression(tokens, pos + 1)
        
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")
            
        if tokens[pos] in ['AND', 'OR']:
            operator = tokens[pos]
            right_node, pos = parse_expression(tokens, pos + 1)
            return Node(type='operator', value=operator, left=left_node, right=right_node), pos
            
        return left_node, pos
        
    if tokens[pos] == ')':
        return None, pos + 1
        
    attribute = tokens[pos]
    operator = tokens[pos + 1]
    value = tokens[pos + 2]
    
    leaf_node = Node(type='operand', value=f"{attribute} {operator} {value}")
    return leaf_node, pos + 3

# Node Evaluation function
def evaluate_node(node: Node, data: Dict) -> bool:
    if node.type == 'operand':
        attr, op, val = node.value.split()
        actual_val = data.get(attr)
        
        try:
            if val.isdigit():
                val = int(val)
                actual_val = int(actual_val)
            elif val.replace('.', '').isdigit():
                val = float(val)
                actual_val = float(actual_val)
        except (ValueError, TypeError):
            pass
            
        if op == '>':
            return actual_val > val
        elif op == '<':
            return actual_val < val
        elif op == '=':
            return actual_val == val.strip("'")
        
    elif node.type == 'operator':
        left_result = evaluate_node(node.left, data)
        right_result = evaluate_node(node.right, data)
        
        if node.value == 'AND':
            return left_result and right_result
        elif node.value == 'OR':
            return left_result or right_result
            
    return False

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# API Routes
@app.route('/api/rules', methods=['POST'])
def create_rule():
    data = request.json
    rule_string = data.get('rule_string')
    rule_name = data.get('name', 'Unnamed Rule')
    
    try:
        tokens = tokenize(rule_string)
        ast_root, _ = parse_expression(tokens)
        
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        
        c.execute(
            'INSERT INTO rules (name, rule_string, ast_json) VALUES (?, ?, ?)',
            (rule_name, rule_string, json.dumps(ast_root.__dict__))
        )
        
        conn.commit()
        rule_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'id': rule_id,
            'message': 'Rule created successfully',
            'ast': ast_root.__dict__
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/rules/evaluate', methods=['POST'])
def evaluate_rule():
    data = request.json
    rule_id = data.get('rule_id')
    user_data = data.get('data')
    
    try:
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        
        c.execute('SELECT ast_json FROM rules WHERE id = ?', (rule_id,))
        result = c.fetchone()
        
        if not result:
            return jsonify({'error': 'Rule not found'}), 404
            
        ast_dict = json.loads(result[0])
        
        def dict_to_node(d):
            if d is None:
                return None
            return Node(
                type=d['type'],
                value=d['value'],
                left=dict_to_node(d['left']),
                right=dict_to_node(d['right'])
            )
            
        ast_root = dict_to_node(ast_dict)
        evaluation_result = evaluate_node(ast_root, user_data)
        
        return jsonify({
            'result': evaluation_result,
            'data': user_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/rules/combine', methods=['POST'])
def combine_rules():
    data = request.json
    rule_ids = data.get('rule_ids', [])
    
    try:
        conn = sqlite3.connect('rules.db')
        c = conn.cursor()
        
        rules_ast = []
        for rule_id in rule_ids:
            c.execute('SELECT ast_json FROM rules WHERE id = ?', (rule_id,))
            result = c.fetchone()
            if result:
                ast_dict = json.loads(result[0])
                rules_ast.append(ast_dict)
        
        combined_ast = None
        for ast_dict in rules_ast:
            if combined_ast is None:
                combined_ast = ast_dict
            else:
                combined_ast = {
                    'type': 'operator',
                    'value': 'AND',
                    'left': combined_ast,
                    'right': ast_dict
                }
        
        return jsonify({
            'combined_ast': combined_ast
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
