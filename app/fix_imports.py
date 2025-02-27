import os
import re

def fix_imports(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Fix relative imports
                content = re.sub(r'from \.\.([\w\.]+)', r'from \1', content)
                content = re.sub(r'from \.([\w\.]+)', r'from \1', content)
                
                with open(filepath, 'w') as f:
                    f.write(content)

if __name__ == '__main__':
    fix_imports('.')