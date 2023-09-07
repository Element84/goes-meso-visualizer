example: build/web-png.json
	@mkdir -p site
	goes-meso-visualizer build build/web-png.json src/goes_meso_visualizer/ep092023_best_track.json index.html site
.PHONY: example

serve-example:
	which http-server || npm install --global http-server
	http-server site
.PHONY: serve-example

build/web-png.json: build/colorized.json
	goes-meso-visualizer web-png $< $@

build/colorized.json: build/solarized.json
	goes-meso-visualizer colorize $< $@

build/solarized.json: build/downloaded.json
	goes-meso-visualizer solarize $< $@

build/downloaded.json: build/search.json
	goes-meso-visualizer download $< $@

build/search.json:
	@mkdir -p $(dir $@)
	goes-meso-visualizer search \
		src/goes_meso_visualizer/ep092023_best_track.json \
		--start 2023-08-16 \
		--end 2023-08-21  > $@
