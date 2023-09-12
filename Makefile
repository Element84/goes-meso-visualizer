example: build/web-png.json
	@mkdir -p site
	goes-meso-visualizer build build/web-png.json src/goes_meso_visualizer/ep092023_best_track.json site
.PHONY: example

serve-example:
	which http-server || npm install --global http-server
	http-server site
.PHONY: serve-example

sync-example: example
	aws s3 sync site s3://e84-gadomski-hilary-demo
.PHONY: sync examplte

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

build/lee/al132023_best_track.zip:
	@mkdir -p $(dir $@)
	curl -s https://www.nhc.noaa.gov/gis/best_track/al132023_best_track.zip > $@

build/lee/al132023_best_track.json: build/lee/al132023_best_track.zip
	ogr2ogr $@ /vsizip/$< AL132023_lin -f GeoJSON

build/lee/search.json: build/lee/al132023_best_track.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer search $< \
		--start 2023-09-06 \
		--end 2023-09-09  > $@

build/lee/web-png.json: build/lee/colorized.json
	goes-meso-visualizer web-png $< $@

build/lee/colorized.json: build/lee/solarized.json
	goes-meso-visualizer colorize $< $@

build/lee/solarized.json: build/lee/downloaded.json
	goes-meso-visualizer solarize $< $@

build/lee/downloaded.json: build/lee/search.json
	goes-meso-visualizer download $< $@
