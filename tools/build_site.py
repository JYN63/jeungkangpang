# 게임 원본(osaekpang.html)으로 웹사이트 index.html을 만든다.
# 사용: python3 tools/build_site.py <osaekpang.html 경로> [버전]
#  - 구글 글꼴 중 한·영·이 글꼴은 사이트 안의 fonts/로 바꾼다(오프라인에서도 같은 글꼴)
#  - 검색(구글·네이버)용 머리말, 홈 화면 앱(PWA) 설정, Firebase 랭킹 설정을 넣는다
#  - sw.js의 캐시 이름을 버전에 맞춰 바꾼다(홈 화면 앱이 새 버전을 받도록)
import sys, re, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = sys.argv[1]; ver = sys.argv[2] if len(sys.argv) > 2 else 'dev'
cfg = json.load(open(os.path.join(ROOT, 'site.json'), encoding='utf-8'))
URL = cfg['url'].rstrip('/') + '/'
src = open(src_path, encoding='utf-8').read()
old_link = '<link href="https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&family=Fredoka:wght@500;600&family=Nunito:wght@500;700&family=M+PLUS+Rounded+1c:wght@500;800&family=ZCOOL+KuaiLe&family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">'
assert src.count(old_link) == 1
new_link = '<link href="fonts/fonts.css" rel="stylesheet">\n<link href="https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;800&family=ZCOOL+KuaiLe&family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">'
src = src.replace(old_link, new_link).replace('<title>증강팡 · Augment Pop</title>', '')
title = '증강팡 - 무료 매치3 퍼즐 게임 | Augment Pop'
desc = '증강팡은 애니팡처럼 같은 색 타일을 맞춰 터뜨리고, 증강을 골라 더 멀리 가는 무료 매치-3 퍼즐 게임이에요. 1분 모드, 무한 모드, 한옥 테마와 국악 배경음악까지. 설치 없이 휴대폰 브라우저에서 바로 즐기세요.'
ld = {"@context": "https://schema.org", "@type": "VideoGame", "name": "증강팡", "alternateName": ["Augment Pop", "jeungkangpang"], "url": URL,
      "description": desc, "genre": ["Puzzle", "Match 3"], "gamePlatform": ["Web browser", "Android", "iOS"], "applicationCategory": "Game",
      "operatingSystem": "Any", "inLanguage": ["ko", "en", "ja", "zh", "it"], "author": {"@type": "Person", "name": "이정연"},
      "image": URL + "icon-512.png", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "KRW"}}
verify = ''.join(f'<meta name="{k}" content="{v}">' for k, v in cfg.get('verify', {}).items() if v)
fire = json.dumps(cfg.get('firebase')) if cfg.get('firebase', {}).get('apiKey') else 'null'
head = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{URL}">
<meta name="theme-color" content="#a9d8ff">
<meta property="og:type" content="website"><meta property="og:site_name" content="증강팡"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="{URL}"><meta property="og:image" content="{URL}icon-512.png"><meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary">{verify}
<link rel="manifest" href="manifest.webmanifest"><link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="apple-mobile-web-app-title" content="증강팡">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script>window.JKP_FIREBASE = {fire};</script>
<style>html{{-webkit-text-size-adjust:100%}}body{{margin:0;font:14px system-ui,sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}.seo{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}</style></head><body>
<h1 class="seo">증강팡 (Augment Pop)</h1><p class="seo">{desc}</p>
<noscript><h1>증강팡</h1><p>{desc}</p><p>자바스크립트를 켜야 게임을 할 수 있어요.</p></noscript>'''
tail = '''
<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
</script>
</body></html>'''
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(head + src.rstrip('\n') + tail)
sw = open(os.path.join(ROOT, 'sw.js'), encoding='utf-8').read()
sw = re.sub(r"const CACHE = '[^']*';", f"const CACHE = 'jkp-{ver}';", sw)
open(os.path.join(ROOT, 'sw.js'), 'w', encoding='utf-8').write(sw)
open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {URL}sitemap.xml\n')
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc><changefreq>weekly</changefreq><priority>1.0</priority></url></urlset>\n')
print('built', ver, URL, 'firebase' if fire != 'null' else 'no-firebase')
