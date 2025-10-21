import json
import os
import random
from collections import namedtuple

from PIL import Image, ImageOps

from logger.logger import Logger

logger = Logger()

# TODO rename to class name
# TODO make main that runs the comandline command
# TODO add arguments so that quiet, batchsize, path, log etc can be spcified
# TODO add pause after running
# TODO finish other todos
# TODO build to exe
# TODO upload to github
# TODO add to portfolio

class BingoCard:
	# MARK: Named Tuples
	BoardShape = namedtuple('BoardShape', 'cols rows')
	CardSize = namedtuple('CardSize', 'width hight')
	TileSize = namedtuple('TileSize', 'width hight')
	Cord = namedtuple('Cord', 'x y')

	# MARK: Defualt Config
	configFilePath: str = "config.json"
	name: str = "Bingo Card Maker"
	description: str = "Config Load failed"
	poolDirectoryPath: str = "pool"
	baseImagePath: str = "base.png"
	freespaceImagePath: str = "freespace.png"
	outputPath: str = "output"
	boardShape: BoardShape = BoardShape(5,5)
	numTiles = boardShape.cols * boardShape.rows
	hasFreespace: bool = True
	freespaceIndex: int = 12
	cardSize: CardSize = CardSize(1000,1000)
	tileSize: TileSize = TileSize(50,50)
	tileStartCor: Cord = Cord(50,50)
	tilepading: int = 5
	useBaseImage: bool = True
	numOfCardsInBatch: int = 5
	imageFileType: str = "PNG"
	bgColor: tuple = (255,255,255,255)

	def __init__(self, configFilePath="config.json"):
		log = logger.addTag("init BingoCard")
		# MARK: Load Config
		try:
			log.dbg(f"Opening config file {configFilePath}")
			self.fp = open(configFilePath, "r")
			self.config = json.load(self.fp)
			log.dbg("loaded json")
			self.name = self.config["name"]
			self.description = self.config["description"]
			self.poolDirectoryPath = self.config["poolDirectoryPath"]
			self.baseImagePath = self.config["baseImagePath"]
			self.freespaceImagePath = self.config["freespaceImagePath"]
			self.outputPath = self.config["outputPath"]
			log.dbg("Trying to load boardshape")
			self.boardShape = self.BoardShape(
				self.config["boardShape"][0],
				self.config["boardShape"][1]
			)
			log.dbg("Loaded boardshape")
			self.hasFreespace = self.config["hasFreespace"]
			self.cardSize = self.CardSize(
				self.config["cardSize"][0],
				self.config["cardSize"][1]
			)
			self.tileSize = self.TileSize(
				self.config["tileSize"][0],
				self.config["tileSize"][1],
			)
			self.tileStartCor = self.Cord(
				self.config["tileStartCor"][0],
				self.config["tileStartCor"][1],
			)
			self.tilepading = self.config["tilepading"]
			self.useBaseImage = self.config["useBaseImage"]
			self.numOfCardsInBatch = self.config["numOfCardsInBatch"]
			self.imageFileType = self.config["imageFileType"]
			self.bgColor = tuple(self.config["bgColor"])
		except Exception as e:
			log.err("Loading the config failed")
			log.err(str(e))
		
		log.inf(self.name)
		log.inf(self.description)

	# scan the pool dir and collect all the pngs
	# TODO user imageFileType
	def loadpool(self, poolDirectoryPath: str=None) -> []:
		log = logger.addTag("loadpool")
		log.inf("Loading pool")
		pool = []

		if poolDirectoryPath is None:
			poolDirectoryPath = self.poolDirectoryPath
		with os.scandir(poolDirectoryPath) as poolDir:
			for e in poolDir:
				log.dbg(e.name)
				if e.name.endswith(".png"):
					pool.append(e)
		
		log.inf("Found {} tiles in pool".format(len(pool)))

		return pool

	# returns a PIL image of a randomized card
	def createCard(self, pool) -> Image:
		log = logger.addTag("createCard")
		log.inf("Creating Card")

		# Randomize the list of pool cards and pick row x col amount of them
		random.shuffle(pool)
		cardTiles = []
		for i in range(self.numTiles):
			cardTiles.append(pool[i])

		# if the card has a free space it needs on less tile
		if self.hasFreespace:
			log.dbg("Removing Free Space")
			cardTiles.pop()
		
		log.inf("Pulled {} tiles from the pool".format(len(cardTiles)))

		# create the card image
		cardimg = Image.new("RGBA", self.cardSize, self.bgColor)

		# TODO resize and copy the base image

		# TODO draw boarders

		# draw the tiles other than the free space
		for i, t in enumerate(cardTiles):
			if i >= self.freespaceIndex:
				i += 1
			
			with Image.open(t.path).convert("RGBA") as im:
				resized = ImageOps.fit(im, self.tileSize)
				xpos = (((i % self.boardShape.cols) * (self.tileSize.width
					+ self.tilepading))
					+ self.tilepading + self.tileStartCor.x)
				ypos = ((int(i/self.boardShape.cols) * (self.tileSize.hight
					+ self.tilepading))
					+ self.tilepading + self.tileStartCor.y)
				
				cardimg.paste(resized,(xpos, ypos), resized)
		
		# draw the free space

		log.dbg("Draw freespace")
		with Image.open(self.freespaceImagePath) as im:
			resized = ImageOps.fit(im, self.tileSize)
			xpos = (((self.freespaceIndex % self.boardShape.cols) * (self.tileSize.width
				+ self.tilepading))
				+ self.tilepading + self.tileStartCor.x)
			ypos = ((int(self.freespaceIndex/self.boardShape.cols) * (self.tileSize.hight
				+ self.tilepading))
				+ self.tilepading + self.tileStartCor.y)
			
			cardimg.paste(resized,(xpos, ypos), resized)
		
		# TODO add author infomation

		# TODO add qr code for link



		return cardimg

	# Saves img to output dir
	def saveCard(self, cardimg, name) -> None:
		log = logger.addTag("saveCard")
		try:
			outfile = os.path.join(self.outputPath, (name + ".png"))
			log.inf("Saving card {}".format(outfile))
			cardimg.save(outfile, self.imageFileType)
		except:
			log.err("Failed to save card")

	# generates and saves multiple cards with numbered names
	def genBatchOfCards(self, pool = None):
		log = logger.addTag("genBatchOfCards")
		log.inf("Starting")

		if pool is None:
			pool = self.loadpool()
		for i in range(self.numOfCardsInBatch):
			cardimg = self.createCard(pool)
			self.saveCard(cardimg, "card{}".format(i))
		
		log.inf("Generation Complete")



# MARK: Main
def main():

	bingoCard = BingoCard()


	bingoCard.genBatchOfCards()


	

if __name__ == '__main__':
	main()