import urllib.request
import json
import gzip
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://kaikki.org/dictionary/Turkish/kaikki.org-dictionary-Turkish.jsonl'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip'})

print("Connecting to Kaikki Turkish...")
with urllib.request.urlopen(req, timeout=15) as resp:
    with gzip.GzipFile(fileobj=resp) as gz:
        shown = 0
        for line in gz:
            data = json.loads(line.decode('utf-8'))
            w = data.get('word', '')
            pos = data.get('pos', '')
            senses = data.get('senses', [])
            
            # Filter out pure inflections like "ablative singular of..."
            lemma_senses = []
            for s in senses:
                tags = s.get('tags') or []
                if 'form-of' in tags:
                    continue
                glosses = s.get('glosses', [])
                if glosses:
                    lemma_senses.append((glosses[0], tags))
            
            if len(lemma_senses) >= 2:
                print(f"\n{w} [{pos}]:")
                for gloss, tags in lemma_senses[:4]:
                    print(f"   - {gloss} (tags: {tags})")
                shown += 1
                if shown >= 15:
                    break
