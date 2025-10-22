import sys
import os

from PIL import Image, ImageDraw

from logger.logger import Logger

log = Logger()

def main():
	
	outputPath: str = "pool"
	tileSize: tuple = (256, 256)
	tileBG: tuple = (255,255,255,0)
	tileGen: str = "RANGE"
	tileRange: tuple = (1, 30)
	textColor: tuple = (0,0,0,255)
	textSize: int = 200

	log.dbg(f"Total arguments: {len(sys.argv)}")
	log.dbg(f"Script name: {sys.argv[0]}")
	log.dbg(f"Arguments: {sys.argv[1:]}")

	# get/make output dir

	# get size

	# get list of tiles to make

	# Loop through list
	if tileGen == "RANGE":
		log.inf(f"Generating range tiles {tileRange[0]}:{tileRange[1]}")
		for i in range(tileRange[0], tileRange[1]):
			im = Image.new("RGBA", tileSize, tileBG)
			draw = ImageDraw.Draw(im)
			draw.multiline_text((tileSize[0]/2,tileSize[1]/2), str(i),textColor, anchor="mm", align="center", font_size=textSize)

			try:
				log.dbg(f"Saving {i}")
				outfile = os.path.join(outputPath, f"{i}.png")
				im.save(outfile, "PNG")
			except Exception as e:
				log.err("Failed to save tile")
				log.err(str(e))



	# make new image/drawer

	# draw text to image

	# save to output dir

if __name__ == '__main__':
	main()
