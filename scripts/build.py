"""Build the static archive using only the Python standard library."""
import json
from pathlib import Path
from html import escape
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
events = json.loads((ROOT / 'data/events.json').read_text(encoding='utf-8'))
events.sort(key=lambda e: (e['date'], e['time']))
assert len({e['id'] for e in events}) == len(events), 'Duplicate event IDs'
parts = []
year = None
for e in events:
    if year != e['date'][:4]:
        year = e['date'][:4]
        parts.append(f'<h2 class="year-heading" id="year-{year}"><span>{year}</span><small>开发记录</small></h2>')
    dt = datetime.fromisoformat(e['date'])
    images = []
    for n in e['images']:
        filename = f'assets/image{n}.jpeg'
        assert (ROOT / filename).is_file(), filename
        label = f"{e['title']} · {'图标' if n == e.get('icon') else '原始记录'}"
        images.append(f'<a class="image-link {"icon-image" if n == e.get("icon") else ""}" href="{filename}" data-caption="{escape(label)}" aria-label="查看{escape(label)}"><img src="{filename}" alt="{escape(label)}" loading="lazy" width="180" height="144"><span>{"图标" if n == e.get("icon") else "原图"} ↗</span></a>')
    note = f'<p class="record-note">{escape(e["note"])}</p>' if e.get('note') else ''
    media = f'<div class="event-images">{"".join(images)}</div>' if images else ''
    parts.append(f'''<article class="event" id="{e['id']}" data-category="{escape(e['category'])}" data-year="{year}">
      <div class="event-date"><time datetime="{e['date']}T{e['time']}"><span>{dt:%m.%d}</span><small>{e['time']}</small></time></div>
      <div class="event-body"><span class="category">{escape(e['category'])}</span><h3><a href="#{e['id']}">{escape(e['title'])}</a></h3><p>{escape(e['text'])}</p>{note}{media}
        <details class="source"><summary>查看原文记录</summary><p>{escape(e['source'])}</p></details>
      </div>
    </article>''')
template = (ROOT / 'scripts/page.html').read_text(encoding='utf-8')
(ROOT / 'index.html').write_text(template.replace('<!-- EVENTS -->', '\n'.join(parts)).replace('{{COUNT}}', str(len(events))), encoding='utf-8')
print(f'Built index.html: {len(events)} events, {sum(len(e["images"]) for e in events)} images.')
