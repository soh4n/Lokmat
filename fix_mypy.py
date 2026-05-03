import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to only add -> None if it's missing
    lines = content.split('\n')
    changed = False
    for i in range(len(lines)):
        line = lines[i]
        # Ignore comments and decorators
        if line.strip().startswith('#') or line.strip().startswith('@'):
            continue
            
        if line.strip().startswith('def ') or line.strip().startswith('async def '):
            if '->' not in line and line.endswith(':'):
                lines[i] = line[:-1] + ' -> None:'
                changed = True
        
        # fix returning Any where specific type declared 
        # For simplicity, we just change `-> Any` to the right type or let mypy handle it.
        # Actually, let's fix missing generics
        if 'dict[' not in line and re.search(r'\bdict\b', line) and not line.strip().startswith('import'):
            # only if it's a type hint
            if ':' in line or '->' in line:
                pass # too risky with regex
                
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

for root, _, files in os.walk('api'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))

for root, _, files in os.walk('tests'):
    for file in files:
        if file.endswith('.py'):
            fix_file(os.path.join(root, file))
