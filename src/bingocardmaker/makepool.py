import sys

from logger.logger import Logger

log = Logger()

def main():
	
	tileSize: tuple = (256, 256)
	tileBG: tuple = (255,255,255,0)
	tileGen: str = "RANGE"
	textColor: tuple = (0,0,0,255)

	log.dbg(f"Total arguments: {len(sys.argv)}")
	log.dbg(f"Script name: {sys.argv[0]}")
	log.dbg(f"Arguments: {sys.argv[1:]}")

	# get/make output dir

	# get size

	# get list of tiles to make

	# Loop through list

	# make new image/drawer

	# draw text to image

	# save to output dir

if __name__ == '__main__':
	main()
