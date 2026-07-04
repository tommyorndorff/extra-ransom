.PHONY: build serve clean

build:
	hugo

serve:
	hugo server --buildDrafts

clean:
	rm -rf public resources/_gen
