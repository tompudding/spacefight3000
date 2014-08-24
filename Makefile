all:
	python spacefight3000.py

sprites:
	python atlas.py -s 2048 -o tiles_atlas resource/sprites/*.png
