## Scrape Martin Fowler's Bliki

Code based on "Ask TW" PoC (by Thomas Kunze and David Guijjaro), [original code here](https://github.com/twlabs/tw-public-knowledge-data)

- `python knowledge_scripts/mfcom/extract.py`: scrapes entries of Martin's /bliki based on `tags_all.yaml`
- `python knowledge_scripts/mfcom/index.py`: Takes results of the extract script and indexes them with FAISS
