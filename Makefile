.PHONY: help build serve clean
.DEFAULT_GOAL := help

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk -F ':.*## ' '{printf "  make %-8s %s\n", $$1, $$2}'

build: ## Build the site into public/
	hugo

serve: ## Run the dev server with drafts at http://localhost:1313
	hugo server --buildDrafts

clean: ## Remove public/ and resources/_gen/
	rm -rf public resources/_gen
