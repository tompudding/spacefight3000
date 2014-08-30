all:
	python spacefight3000.py

sprites:
	python atlas.py -s 2048 -o tiles_atlas resource/sprites/*.png

video:
	gource --user-image-dir gource-resources -w -1920x1080 -i 0 -o - -s 20 --background-image gource-resources/starfield.png -t 60 -r 60 | avconv -y -r 60 -f image2pipe -vcodec ppm -i - -i resource/music/title_music.ogg -map 0 -map 1 -c:a libmp3lame -c:v h264 -b 8192K -shortest movie.mp4

