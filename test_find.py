
with open('build_dashboard_gerencial.py', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'projection-grid' in line:
            print(f'Line {i+1}: {line}')
