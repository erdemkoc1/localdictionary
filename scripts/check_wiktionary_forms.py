import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

total_forms = 0
clean_forms = set()
with open('data/wiktionary_tr_en.tsv', 'r', encoding='utf-8') as f:
    for line in f:
        head_part = line.split('\t')[0]
        forms = head_part.split('|')
        total_forms += len(forms)
        for form in forms:
            f_clean = form.strip().lower()
            if ' ' not in f_clean and '?' not in f_clean and "'" not in f_clean and 2 <= len(f_clean) <= 30:
                clean_forms.add(f_clean)

print('Total forms in file:', total_forms)
print('Unique clean single-word forms:', len(clean_forms))
for test_w in ['geldi', 'gitti', 'okulda', 'evde', 'evden', 'kitaplar', 'baktı', 'yaptı', 'aradım', 'konuştu', 'severim']:
    print(test_w, 'present?', test_w in clean_forms)
