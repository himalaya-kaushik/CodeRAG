# file: parser_fixed.py

import os
import ast
import json
import subprocess
import warnings

warnings.filterwarnings("ignore")

repo_url = ''
clone_dir = repo_url.split('/')[-1].replace('.git', '_codebase')

if not os.path.exists(clone_dir):
    subprocess.run(['git', 'clone', repo_url, clone_dir])

python_files = []
readme_content = ""

for root, dirs, files in os.walk(clone_dir):
    for file in files:
        if file.endswith(".py"):
            python_files.append(os.path.join(root, file))
        elif file.lower() == "readme.md":
            with open(os.path.join(root, file), "r", encoding="utf-8") as readme_file:
                readme_content = readme_file.read()


class CodeParser(ast.NodeVisitor):
    def __init__(self, file_path):
        self.file_path = file_path
        self.functions_classes = []
        self.imports = []
        self.calls = []
        self.global_variables = []
        self.class_methods = {}
        self.imported_functions = {}
        self.function_references = {}

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
                self.imported_functions[alias.name] = node.module
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        function_data = {
            "type": "Function",
            "name": f"{self.file_path}::{node.name}",
            "start_line": node.lineno,
            "end_line": getattr(node, 'end_lineno', node.lineno),
            "code": ast.unparse(node),
            "docstring": ast.get_docstring(node),
            "calls": [],
            "inline_comments": []
        }

        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                function_data["calls"].append(child.func.id)
                self.function_references.setdefault(child.func.id, []).append(self.file_path)
            elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Str):
                function_data["inline_comments"].append(child.value.s)

        self.functions_classes.append(function_data)
        self.calls.append({"caller": function_data["name"], "calls": function_data["calls"]})
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        class_data = {
            "type": "Class",
            "name": f"{self.file_path}::{node.name}",
            "start_line": node.lineno,
            "end_line": getattr(node, 'end_lineno', node.lineno),
            "methods": [],
            "docstring": ast.get_docstring(node),
            "code": ast.unparse(node)
        }

        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                method_name = f"{node.name}.{child.name}"
                class_data["methods"].append(method_name)
                self.class_methods[method_name] = f"{self.file_path}::{node.name}"

        self.functions_classes.append(class_data)
        self.generic_visit(node)

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            self.global_variables.append(node.targets[0].id)
        self.generic_visit(node)

    def parse(self, content):
        try:
            tree = ast.parse(content)
            self.visit(tree)

            # ✅ Add fallback script if nothing parsed
            if not self.functions_classes:
                self.functions_classes.append({
                    "type": "Script",
                    "name": f"{self.file_path}",
                    "start_line": 1,
                    "end_line": len(content.splitlines()),
                    "code": content,
                    "docstring": "",
                    "calls": [],
                    "inline_comments": []
                })

            return {
                "functions_classes": self.functions_classes,
                "imports": self.imports,
                "calls": self.calls,
                "global_variables": self.global_variables,
                "class_methods": self.class_methods,
                "imported_functions": self.imported_functions,
                "function_references": self.function_references
            }

        except SyntaxError:
            return {}


parsed_data = {}
for py_file in python_files:
    with open(py_file, 'r', encoding='utf-8') as f:
        content = f.read()
    parser = CodeParser(py_file)
    parsed_data[py_file] = parser.parse(content)

final_output = {
    "README": readme_content,
    "parsed_code": parsed_data
}

with open('parsed_code.json', 'w', encoding='utf-8') as json_file:
    json.dump(final_output, json_file, indent=2)

print(" Parsing complete! All files (including script-only) saved in 'parsed_code.json'")
