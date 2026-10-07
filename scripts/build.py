"""Build the static archive using only the Python standard library."""
import json
import re
from pathlib import Path
from html import escape
from datetime import datetime
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
events = json.loads((ROOT / 'data/events.json').read_text(encoding='utf-8'))
events.sort(key=lambda e: (e['date'], e.get('time') or '24:00'))
assert len({e['id'] for e in events}) == len(events), 'Duplicate event IDs'
parts = []
year = None
for e in events:
    if year != e['date'][:4]:
        year = e['date'][:4]
        parts.append(f'<h2 class="year-heading" id="year-{year}"><span>{year}</span><small>开发记录</small></h2>')
    dt = datetime.fromisoformat(e['date'])
    timestamp = f'{e["date"]}T{e["time"]}' if e.get('time') else e['date']
    time_label = e.get('time') or '时间未知'
    images = []
    for item in e['images']:
        n = item['file'] if isinstance(item, dict) else item
        crop = item.get('crop') if isinstance(item, dict) else None
        filename = f'assets/image{n}.jpeg' if isinstance(n, int) else f'assets/{n}'
        assert (ROOT / filename).is_file(), filename
        label = f"{e['title']} · {'消息节选' if crop else '图标' if n == e.get('icon') else '原始记录'}"
        attrs = ''
        extra_class = 'icon-image' if n == e.get('icon') else ''
        picture = f'<img src="{filename}" alt="{escape(label)}" loading="lazy" width="180" height="144">'
        if crop:
            assert crop['width'] > 0 and crop['height'] > 0 and crop['y'] >= 0
            ratio = f'{crop["width"]}/{crop["height"]}'
            offset = f'{-crop["y"] / crop["height"] * 100:.6f}%'
            attrs = f' data-crop-ratio="{ratio}" data-crop-offset="{offset}" style="--slice-ratio:{ratio};--slice-top:{offset}"'
            extra_class = 'slice-link'
            picture = f'<span class="image-slice">{picture}</span>'
        badge = '消息节选' if crop else '图标' if n == e.get('icon') else '原图'
        images.append(f'<a class="image-link {extra_class}" href="{filename}" data-caption="{escape(label)}" aria-label="查看{escape(label)}"{attrs}>{picture}<span>{badge} ↗</span></a>')
    note = f'<p class="record-note">{escape(e["note"])}</p>' if e.get('note') else ''
    media = f'<div class="event-images">{"".join(images)}</div>' if images else ''
    video = ''
    if e.get('video'):
        filename = f'assets/{e["video"]}'
        assert (ROOT / filename).is_file(), filename
        video = f'''<figure class="event-video"><video controls playsinline preload="metadata" aria-label="{escape(e['title'])}测试视频"><source src="{escape(filename)}" type="video/mp4"><p>浏览器不支持视频播放，请<a href="{escape(filename)}">打开原视频</a>。</p></video><figcaption><span>原型初测录像</span><a href="{escape(filename)}" download>下载视频 ↓</a></figcaption></figure>'''
    parts.append(f'''<article class="event" id="{e['id']}" data-category="{escape(e['category'])}" data-year="{year}">
      <div class="event-date"><time datetime="{timestamp}"><span>{dt:%m.%d}</span><small>{time_label}</small></time></div>
      <div class="event-body"><span class="category">{escape(e['category'])}</span><h3><a href="#{e['id']}">{escape(e['title'])}</a></h3><p>{escape(e['text'])}</p>{note}{media}{video}
        <details class="source"><summary>查看原文记录</summary><p>{escape(e['source'])}</p></details>
      </div>
    </article>''')
template = (ROOT / 'scripts/page.html').read_text(encoding='utf-8')
year_counts = Counter(e['date'][:4] for e in events)
year_nav = ''.join(f'<a href="#year-{y}">{y} <span>{n:02d}</span></a>' for y, n in sorted(year_counts.items()))
image_count = len({item['file'] if isinstance(item, dict) else item for e in events for item in e['images']})
video_count = sum(bool(e.get('video')) for e in events)
page = template.replace('<!-- EVENTS -->', '\n'.join(parts)).replace('{{COUNT}}', str(len(events))).replace('{{IMAGE_COUNT}}', str(image_count)).replace('{{VIDEO_COUNT}}', str(video_count)).replace('<!-- YEAR NAV -->', year_nav)
page = re.sub(r'<a(?=\s)(?![^>]*\bclass="image-link\b)(?![^>]*\bdraggable=)', '<a draggable="false"', page)
(ROOT / 'index.html').write_text(page, encoding='utf-8')
print(f'Built index.html: {len(events)} events, {image_count} images, {video_count} videos.')
