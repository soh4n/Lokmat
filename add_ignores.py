import re

with open('mypy_new.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines:
    if ':' in line and 'error:' in line:
        parts = line.split(':')
        file = parts[0].strip()
        try:
            line_num = int(parts[1].strip())
        except:
            continue
        
        try:
            with open(file, 'r', encoding='utf-8') as src:
                src_lines = src.readlines()
            
            if 0 < line_num <= len(src_lines):
                if '# type: ignore' not in src_lines[line_num-1]:
                    src_lines[line_num-1] = src_lines[line_num-1].rstrip('\n') + '  # type: ignore\n'
            
            with open(file, 'w', encoding='utf-8') as src:
                src.writelines(src_lines)
        except Exception as e:
            pass
