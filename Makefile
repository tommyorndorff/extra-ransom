.PHONY: build serve clean

build:
	hugo --theme=hugo-book

serve:
	hugo server --theme=hugo-book --buildDrafts

clean:
	rm -rf public resources/_gen
