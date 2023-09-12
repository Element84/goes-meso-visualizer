site: site/hilary/index.html site/lee/index.html
.PHONY: site

searches: searches/hilary.json searches/lee.json
.PHONY: searches

tracks: src/goes_meso_visualizer/tracks/al132023_best_track.json src/goes_meso_visualizer/tracks/ep092023_best_track.json
.PHONY: tracks

site/%/index.html: build/%/web_png.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer build $< searches/$*.json site/$*

build/%/web_png.json: build/%/colorized.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer web-png $< $@

build/%/colorized.json: build/%/solarized.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer colorize $< $@

build/%/solarized.json: build/%/downloaded.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer solarize $< $@

build/%/downloaded.json: searches/%.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer download $< $@

searches/hilary.json: src/goes_meso_visualizer/tracks/ep092023_best_track.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer search \
		$< \
		--start 2023-08-17 \
		--end 2023-08-21 \
		--exclude OR_ABI-L2-M1-M6_G18_s20232291800295 > $@

searches/lee.json: src/goes_meso_visualizer/tracks/al132023_best_track.json
	@mkdir -p $(dir $@)
	goes-meso-visualizer search \
		$< \
		--start 2023-09-06 \
		--end 2023-09-17  > $@

src/goes_meso_visualizer/tracks/al132023_best_track.json: build/al132023_best_track.zip
	ogr2ogr $@ /vsizip/$< AL132023_lin -f GeoJSON

src/goes_meso_visualizer/tracks/ep092023_best_track.json: build/ep092023_best_track.zip
	ogr2ogr $@ /vsizip/$< EP092023_lin -f GeoJSON

build/%.zip:
	@mkdir -p $(dir $@)
	curl -s https://www.nhc.noaa.gov/gis/best_track/$*.zip > $@
