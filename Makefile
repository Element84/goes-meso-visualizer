data/goes-cmi.json:
	e84-hilary search $@

assets/goes-cmi.json: data/goes-cmi.json
	e84-hilary download $< $@

assets/goes-cmi-solarized.json: assets/goes-cmi.json
	e84-hilary solarize $< $@

assets/goes-cmi-colorized.json: assets/goes-cmi-solarized.json
	e84-hilary colorize $< $@

assets/goes-cmi-tiled.json: assets/goes-cmi-colorized.json
	e84-hilary tile $< $@

assets/index.html: assets/goes-cmi-tiled.json
	e84-hilary html $< $@

sync:
	aws s3 sync assets s3://e84-gadomski-hilary-demo --exclude '*' --include '*.png' --include 'index.html'
.PHONY: sync
