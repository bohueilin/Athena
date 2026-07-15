GUARDIAN := skills/guardian-agent-foundations

.PHONY: install uninstall validate search help
help:
	@echo "make install    - symlink skills into ~/.claude/skills/ (per machine)"
	@echo "make uninstall  - remove those symlinks"
	@echo "make validate   - run the guardian integrity gates (works without local PDFs)"
	@echo "make search Q='attack prompt_injection'  - query the knowledge base"

install:
	@./install.sh

uninstall:
	@./install.sh --uninstall

validate:
	@python3 $(GUARDIAN)/tests/validate.py

search:
	@python3 $(GUARDIAN)/scripts/search.py $(Q)
