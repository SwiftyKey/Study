import os
from markitdown import MarkItDown
from pathlib import Path

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

md = MarkItDown()
result = md.convert(BASE_DIR / 'book.pdf')
content = result.text_content

output_path = BASE_DIR / 'book.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

processed_document = {
    'source': BASE_DIR / 'book.pdf',
    'content': content,
    'markdown_file': BASE_DIR / 'book.md'
}

documents = [processed_document]

print(f"Document ready: {len(processed_document['content']):,} characters")
print(f"Markdown saved to: {output_path}")
