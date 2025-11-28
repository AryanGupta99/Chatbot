import json

chunks = json.load(open('data/processed/final_chunks.json', 'r', encoding='utf-8'))
print(f'Total chunks available: {len(chunks)}')

doc_chunks = [c for c in chunks if c['metadata'].get('type') != 'training_example']
training_chunks = [c for c in chunks if c['metadata'].get('type') == 'training_example']

print(f'Document chunks: {len(doc_chunks)}')
print(f'Training examples: {len(training_chunks)}')
