import json
import os
import random
from collections import namedtuple

from PIL import Image, ImageOps, ImageDraw
import qrcode

from logger.logger import Logger

logger = Logger()

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
	poolImageTypes: [str] = ["PNG"]
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
	drawBoarder: bool = True
	boarderColor: tuple = (0,0,0,255)
	boarderWidth: int = 4
	drawExtraInfo: bool = True
	extraInfo: str = "This is a bingo randomizer card creater made by Nox Noxtua"
	drawQRCode: bool = True
	qrLink: str = "https://github.com/NoxNoctua/BingoCardMaker"
	qrLocation: str = "BOTTOM_RIGHT"
	drawWatermark: bool = True
	watermarkFilePath: str = "watermark.png"

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
			self.poolImageTypes = self.config["poolImageTypes"]
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
			self.drawBoarder - self.config["drawBoarder"]
			self.boarderColor = tuple(self.config["boarderColor"])
			self.boarderWidth = self.config["boarderWidth"]
			self.drawQRCode = self.config["drawQRCode"]
			self.qrLink = self.config["qrLink"]
			self.qrLocation = self.config["qrLocation"]
			self.drawWatermark = self.config["drawWatermark"]
			self.watermarkFilePath = self.config["watermarkFilePath"]
		except Exception as e:
			log.err("Loading the config failed")
			log.err(str(e))
		
		log.inf(self.name)
		log.inf(self.description)

	# scan the pool dir and collect all the pngs
	def loadpool(self, poolDirectoryPath: str=None) -> []:
		log = logger.addTag("loadpool")
		log.inf("Loading pool")
		pool = []

		if poolDirectoryPath is None:
			poolDirectoryPath = self.poolDirectoryPath
		
		fileEndings = []
		for i in self.poolImageTypes:
			fileEndings.append("."+i.lower())
		fileEndings = tuple(fileEndings)

		try:
			with os.scandir(poolDirectoryPath) as poolDir:
				for e in poolDir:
					log.dbg(e.name)
					if e.name.endswith(fileEndings):
						pool.append(e)
		except Exception as e:
			log.err("Could not scan pool dir")
			log.err(str(e))
			throw(Exception())
		
		log.inf("Found {} tiles in pool".format(len(pool)))

		return pool

	# returns a PIL image of a randomized card
	def createCard(self, pool, id:int=None) -> Image:
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
		draw = ImageDraw.Draw(cardimg)

		# paste in base image
		if self.useBaseImage:
			try:
				with Image.open(self.baseImagePath).convert("RGBA") as im:
					resized = ImageOps.fit(im, self.CardSize)
					cardimg.paste(resized, (0,0), resized)
			except Exception as e:
				log.err("Loading base image failed")
				log.err(str(e))

		# draw boarders
		if self.drawBoarder:
			for i in range(self.numTiles):
				xpos = (
					((i % self.boardShape.cols) *
					(self.tileSize.width + self.tilepading)) +
					self.tileStartCor.x
				)
				ypos = (
					(int(i / self.boardShape.cols) *
					(self.tileSize.hight + self.tilepading)) +
					self.tileStartCor.y
				)
				draw.rectangle(
					(xpos+(self.tilepading/2)-(self.boarderWidth/2),
					ypos+(self.tilepading/2)-(self.boarderWidth/2),
					xpos+self.tileSize.width+(1.5*self.tilepading)+(self.boarderWidth/2),
					ypos+self.tileSize.hight+(1.5*self.tilepading)+(self.boarderWidth/2)),
					outline=self.boarderColor,
					width=self.boarderWidth
				)

		# draw the tiles other than the free space
		for i, t in enumerate(cardTiles):
			if i >= self.freespaceIndex:
				i += 1
			try:
				with Image.open(t.path).convert("RGBA") as im:
					resized = ImageOps.fit(im, self.tileSize)
					xpos = (((i % self.boardShape.cols) * (self.tileSize.width
						+ self.tilepading))
						+ self.tilepading + self.tileStartCor.x)
					ypos = ((int(i/self.boardShape.cols) * (self.tileSize.hight
						+ self.tilepading))
						+ self.tilepading + self.tileStartCor.y)
					
					cardimg.paste(resized,(xpos, ypos), resized)
			except Exception as e:
				log.err("Failed to open tile image")
				log.err(str(e))
		
		# draw the free space
		log.dbg("Draw freespace")
		try:
			with Image.open(self.freespaceImagePath).convert("RGBA") as im:
				resized = ImageOps.fit(im, self.tileSize)
				xpos = (((self.freespaceIndex % self.boardShape.cols) * (self.tileSize.width
					+ self.tilepading))
					+ self.tilepading + self.tileStartCor.x)
				ypos = ((int(self.freespaceIndex/self.boardShape.cols) * (self.tileSize.hight
					+ self.tilepading))
					+ self.tilepading + self.tileStartCor.y)
				
				cardimg.paste(resized,(xpos, ypos), resized)
		except Exception as e:
			log.err("Failed to open freespace png")
			log.err(str(e))
		
		# add extra infomation text
		log.dbg(f"Drawing extra info text: {self.drawExtraInfo}")
		if self.drawExtraInfo:
			if id is not None:
				infoText = self.extraInfo + f" | Card ID: {id}"
			fontSize = 10
			draw.text(
				(20,self.cardSize.hight-(fontSize*2)),
				infoText,
				fill=(0,0,0),
				font_size=fontSize
			)


		# add qr code for link
		log.dbg(f"Drawing qrcode: {self.drawQRCode}")
		if self.drawQRCode:
			qr = qrcode.QRCode(
				version=1,
				error_correction=qrcode.constants.ERROR_CORRECT_L,
				box_size=10,
				border=1
			)
			qr.add_data(self.qrLink)
			qr.make(fit=True)

			qrimg = qr.make_image(fill_color=(0,0,0), back_color=(255,255,255)).convert("RGBA")

			qrpos = (0,0)
			if self.qrLocation == "TOP_LEFT":
				qrpos = (0,0)
			elif self.qrLocation == "TOP_RIGHT":
				qrpos = (
					self.cardSize.width-qrimg.width,
					0
				)
			elif self.qrLocation == "BOTTOM_LEFT":
				qrpos = (
					0,
					self.cardSize.hight-qrimg.height
				)
			else:
				qrpos = (
					self.cardSize.width-qrimg.width,
					self.cardSize.hight-qrimg.height
				)

			cardimg.paste(
				qrimg,
				qrpos,
				qrimg
			)

		# add watermark
		log.dbg(f"Drawing watermark: {self.drawWatermark}")
		if self.drawWatermark:
			try:
				with Image.open(self.watermarkFilePath).convert("RGBA") as im:
					cardimg.paste(im, (0,0), im)
			except Exception as e:
				log.err("Failed to open watermark.png")
				log.err(str(e))

		return cardimg

	# Saves img to output dir
	def saveCard(self, cardimg, name) -> None:
		log = logger.addTag("saveCard")
		try:
			outfile = os.path.join(
				self.outputPath, 
				(name + "." + self.imageFileType.lower())
				)
			log.inf("Saving card {}".format(outfile))
			if self.imageFileType == "JPEG":
				cardimg = cardimg.convert("RGB")
			cardimg.save(outfile, self.imageFileType)
		except Exception as e:
			log.err("Failed to save card")
			log.err(str(e))

	# generates and saves multiple cards with numbered names
	def genBatchOfCards(self, pool = None):
		log = logger.addTag("genBatchOfCards")
		log.inf("Starting")

		if pool is None:
			pool = self.loadpool()
		for i in range(self.numOfCardsInBatch):
			cardimg = self.createCard(pool, i)
			self.saveCard(cardimg, "card{}".format(i))
		
		log.inf("Generation Complete")



# MARK: Main
def main():

	bingoCard = BingoCard()


	bingoCard.genBatchOfCards()


	

if __name__ == '__main__':
	main()