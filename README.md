# Rule Engine with AST

This Flask application serves as a rule engine that allows users to create, evaluate, and combine logical rules using Abstract Syntax Trees (AST). It provides a web interface for easy interaction with the rules.

## Features

- **Create Rules**: Users can define rules in a logical expression format.
- **Evaluate Rules**: Users can evaluate rules against user-defined data.
- **Combine Rules**: Users can combine multiple rules into a single logical expression.

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. **Clone the repository**:
   ```
   git clone https://github.com/gireesh777/Rule-Engine-with-AST.git
   cd Rule-Engine-with-AST
   ```
2. **Set up a virtual environment (optional)**:

```
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**:

```
pip install Flask
```

4. **Run the application**:

```
python app.py
```

5. **Access the application**: Open your web browser and navigate to http://127.0.0.1:5000.

## Usage

**Creating a Rule**:
Navigate to the "Create Rule" section.
Enter a rule name and the logical expression (e.g., age > 30).
Click "Create Rule" to save it.

**Evaluating a Rule**:
Navigate to the "Evaluate Rule" section.
Enter the Rule ID and user data in JSON format (e.g., { "age": 35 }).
Click "Evaluate Rule" to see the evaluation result.

**Combining Rules**:
Navigate to the "Combine Rules" section.
Enter a comma-separated list of Rule IDs (e.g., 1, 2).
Click "Combine Rules" to get the combined AST.

## API Endpoints

**Create a new rule**

```
POST /api/rules
body: {
    "name": "Rule Name",
    "rule_string": "Rule Expression"
}
```

Response: Rule ID and AST.

**Evaluate a rule**

```
POST /api/rules/evaluate
body: {
    "rule_id": RuleID,
    "data": { "key": "value" }
    }
```

Response: Evaluation result.

**Combine multiple rule**

```
POST /api/rules/combine
Body: {
    "rule_ids": [RuleID1, RuleID2, ...]
    }
```

Response: Combined AST.
