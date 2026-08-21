import re
app_js = open('C:/Users/alexp/Documentos_Locales_Backup/Morales plumbing/V.01 web/morales-plumbing-web/app.js', 'r', encoding='utf-8').read()

prices_match = re.search(r'const PB_SERVICE_PRICES = \{(.*?)\};', app_js, re.DOTALL)
if prices_match:
    prices_text = prices_match.group(1)
    
    titles = {}
    for match in re.finditer(r'\"svc_(\d+)_title\":\s*\"(.*?)\"', app_js):
        titles[match.group(1)] = match.group(2)
        
    for i in range(1, 16):
        title = titles.get(str(i), 'Service ' + str(i))
        price_match = re.search(r'\"svc_' + str(i) + r'\":\s*\{(.*?)\}', prices_text)
        if price_match:
            print(f'- {title}: {price_match.group(1)}')
