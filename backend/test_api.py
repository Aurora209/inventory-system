import urllib.request
import json

# 测试API
req = urllib.request.Request('http://127.0.0.1:5000/api/products/non-composite')
response = urllib.request.urlopen(req)
data = json.loads(response.read())

products = data['data']
print(f'API返回产品数量: {len(products)}')

# 检查是否有成品
composite = [p for p in products if p.get('is_composite') == 1]
print(f'其中成品数量: {len(composite)}')

if composite:
    print('\n成品列表:')
    for p in composite:
        print(f"  - {p['name']} (ID: {p['id']}, is_composite: {p['is_composite']})")
else:
    print('\n✓ 没有成品，过滤成功！')

# 显示所有产品
print(f'\n所有产品列表:')
for p in products:
    composite_flag = '❌ 成品' if p.get('is_composite') == 1 else '✓ 非成品'
    print(f"{p['id']}: {p['name'][:30]} - is_composite={p.get('is_composite')} {composite_flag}")
