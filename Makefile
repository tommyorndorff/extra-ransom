.PHONY: serve run

# Astro needs Node >=22.22 (see .nvmrc). If nvm has a Node 22 installed, use it
# regardless of which version the calling shell has active.
NODE22 := $(lastword $(sort $(wildcard $(HOME)/.nvm/versions/node/v22.*/bin)))
ifneq ($(NODE22),)
export PATH := $(NODE22):$(PATH)
endif

# Build the site, then serve dist/ locally (http://localhost:4321).
serve run:
	npm run build
	npm run preview
