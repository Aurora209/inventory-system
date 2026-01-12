import sqlite3

conn = sqlite3.connect('data/inventory.db')
cursor = conn.cursor()

# 获取所有分类
cursor.execute('SELECT id, name, parent_id FROM categories ORDER BY parent_id, id')
categories = cursor.fetchall()

print('所有分类:')
print('ID\t名称\t\t\tparent_id')
print('-' * 60)
for c in categories:
    print(f'{c[0]}\t{c[1]}\t\t\t{c[2]}')

print('\n分类层级结构:')
parents = [c for c in categories if c[2] is None]
print('一级分类:')
for p in parents:
    print(f'  {p[0]}: {p[1]}')
    children = [c for c in categories if c[2] == p[0]]
    if children:
        print(f'    二级分类:')
        for ch in children:
            print(f'      {ch[0]}: {ch[1]}')

# 查看每个分类下的产品
print('\n每个分类下的产品:')
cursor.execute('''
    SELECT c.id, c.name, c.parent_id, COUNT(p.id) as product_count
    FROM categories c
    LEFT JOIN products p ON p.category_id = c.id
    GROUP BY c.id
    ORDER BY c.parent_id, c.id
''')
for row in cursor.fetchall():
    level = '一级' if row[2] is None else '二级'
    print(f'{level}分类 {row[0]}: {row[1]} - {row[3]} 个产品')

# 查看成品所在的分类
print('\n成品所在分类:')
cursor.execute('''
    SELECT p.id, p.name, p.sku, c.name as category_name, c.id as category_id, c.parent_id
    FROM products p
    LEFT JOIN categories c ON p.category_id = c.id
    WHERE p.is_composite = 1
''')
for row in cursor.fetchall():
    print(f'  产品: {row[1]} (ID: {row[0]}, SKU: {row[2]})')
    print(f'    分类: {row[3]} (ID: {row[4]}, parent_id: {row[5]})')

conn.close()
