import json
import os
import random
from collections import namedtuple

from PIL import Image, ImageOps, ImageDraw
import qrcode

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color

from logger.logger import Logger

logger = Logger()

# TODO make main that runs the comandline command
# TODO add arguments so that quiet, batchsize, path, log etc can be spcified
# TODO add pause after running
# TODO build to exe
# TODO add to portfolio

class BingoCard:
	# MARK: Named Tuples
	BoardShape = namedtuple('BoardShape', 'cols rows')
	CardSize = namedtuple('CardSize', 'width hight')
	CardPadding = namedtuple('CardPadding', 'top right bottom left')
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
	cardPadding: CardPadding = CardPadding(0,0,100,0)
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

	def __init__(self, configFilePath="config.json", quiet=False):
		if quiet:
			logger.active = False
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
			self.cardPadding = self.CardPadding(
				self.config["cardPadding"][0],
				self.config["cardPadding"][1],
				self.config["cardPadding"][2],
				self.config["cardPadding"][3]
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
			self.drawBoarder = self.config["drawBoarder"]
			self.boarderColor = tuple(self.config["boarderColor"])
			self.boarderWidth = self.config["boarderWidth"]
			self.drawQRCode = self.config["drawQR"]
			self.qrLink = self.config["qrLink"]
			self.qrLocation = self.config["qrLocation"]
			self.drawWatermark = self.config["drawWatermark"]
			self.watermarkFilePath = self.config["watermarkFilePath"]

			# add card padding to start cords for tiles
			self.tileStartCor = self.Cord(
				self.tileStartCor.x + self.cardPadding.right,
				self.tileStartCor.y + self.cardPadding.top
			)

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
		# MARK: Create Card
		log = logger.addTag("createCard")
		log.inf("Creating Card")

		# Randomize the list of pool cards and pick row x col amount of them
		random.shuffle(pool)
		cardTiles = []

		# make sure the pool has enough tiles to fill the card
		if self.numTiles > len(pool):
			log.err("There is not enough valid tiles in the pool dir")
			raise Exception("There is not enough valid image files in the pool dir")

		for i in range(self.numTiles):
			cardTiles.append(pool[i])

		# if the card has a free space it needs on less tile
		if self.hasFreespace:
			log.dbg("Removing Free Space")
			cardTiles.pop()
		
		log.inf("Pulled {} tiles from the pool".format(len(cardTiles)))

		# create the card image
		outimgSize = (
			self.cardSize.width + self.cardPadding.right + self.cardPadding.left,
			self.cardSize.hight + self.cardPadding.top + self.cardPadding.bottom
		)
		cardimg = Image.new("RGBA", outimgSize, self.bgColor)
		draw = ImageDraw.Draw(cardimg)

		# paste in base image
		if self.useBaseImage:
			try:
				with Image.open(self.baseImagePath).convert("RGBA") as im:
					resized = ImageOps.fit(im, self.cardSize)
					cardimg.paste(
						resized,
						(self.cardPadding.left,self.cardPadding.top),
						resized
					)
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
					(xpos-(self.boarderWidth/2),
					ypos-(self.boarderWidth/2),
					xpos+self.tileSize.width+(self.tilepading)+(self.boarderWidth/2),
					ypos+self.tileSize.hight+(self.tilepading)+(self.boarderWidth/2)),
					outline=self.boarderColor,
					width=self.boarderWidth
				)

		# draw the tiles other than the free space
		for i, t in enumerate(cardTiles):
			if self.hasFreespace and i >= self.freespaceIndex:
				i += 1
			try:
				with Image.open(t.path).convert("RGBA") as im:
					resized = ImageOps.fit(im, self.tileSize)
					xpos = (
						((i % self.boardShape.cols) * (self.tileSize.width
						+ self.tilepading))
						+ int(self.tilepading/2) + self.tileStartCor.x
					)
					ypos = ((int(i/self.boardShape.cols) * (self.tileSize.hight
						+ self.tilepading))
						+ int(self.tilepading/2) + self.tileStartCor.y)
					
					cardimg.paste(resized,(xpos, ypos), resized)
			except Exception as e:
				log.err("Failed to open tile image")
				log.err(str(e))
		
		# draw the free space
		log.dbg("Draw freespace")
		if self.hasFreespace:
			try:
				with Image.open(self.freespaceImagePath).convert("RGBA") as im:
					resized = ImageOps.fit(im, self.tileSize)
					xpos = (((self.freespaceIndex % self.boardShape.cols) * (self.tileSize.width
						+ self.tilepading))
						+ int(self.tilepading/2) + self.tileStartCor.x)
					ypos = ((int(self.freespaceIndex/self.boardShape.cols) * (self.tileSize.hight
						+ self.tilepading))
						+ int(self.tilepading/2) + self.tileStartCor.y)
					
					cardimg.paste(resized,(xpos, ypos), resized)
			except Exception as e:
				log.err("Failed to open freespace png")
				log.err(str(e))
		
		# add extra infomation text
		log.dbg(f"Drawing extra info text: {self.drawExtraInfo}")
		if self.drawExtraInfo:
			if id is not None:
				infoText = self.extraInfo + f" | Card ID: {id}"
			else:
				infoText = self.extraInfo
			fontSize = 10
			draw.text(
				(20+self.cardPadding.left,cardimg.height-(fontSize*2)),
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
				box_size=3,
				border=4
			)
			qr.add_data(self.qrLink)
			qr.make(fit=True)

			qrimg = qr.make_image(fill_color=(0,0,0), back_color=self.bgColor).convert("RGBA")

			qrpos = (0,0)
			if self.qrLocation == "TOP_LEFT":
				qrpos = (self.cardPadding.left,0)
			elif self.qrLocation == "TOP_RIGHT":
				qrpos = (
					cardimg.width-qrimg.width-self.cardPadding.right,
					0
				)
			elif self.qrLocation == "BOTTOM_LEFT":
				qrpos = (
					self.cardPadding.left,
					cardimg.height-qrimg.height
				)
			else:
				qrpos = (
					cardimg.width-qrimg.width-self.cardPadding.right,
					cardimg.height-qrimg.height
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
	def genBatchOfCards(self, pool = None, asPDF=False):
		log = logger.addTag("genBatchOfCards")
		log.inf("Starting")

		if pool is None:
			pool = self.loadpool()
		for i in range(self.numOfCardsInBatch):
			cardimg = self.createCard(pool, i)
			if asPDF or self.imageFileType=="PDF":
				self.saveToPDF(cardimg, "card{}".format(i))
			else:
				self.saveCard(cardimg, "card{}".format(i))
		
		log.inf("Generation Complete")

	# MARK: Converting to interactive pdf
	# Convert image to pdf with checkboxes
	def saveToPDF(self, im: Image, name: str, addCheckboxes: bool=True):
		
		outfile = os.path.join(
			self.outputPath, 
			(name + ".pdf")
		)
		c = canvas.Canvas(
			outfile,
			pagesize=(im.width, im.height)
		)
		c.drawImage(ImageReader(im),0,0)

		c.setFillAlpha(0)
		c.setStrokeAlpha(0)
		if addCheckboxes:
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
				#flip cord for x axis
				ypos = (im.height - ypos) - self.tileSize.hight - self.tilepading
				c.acroForm.checkbox(
					checked=False,
					x=xpos,
					y=ypos,
					size=self.tileSize.width+self.tilepading,
					fillColor=Color(0,0,0,0),
					name=f"TileBox{i}",
					borderWidth=0,
					borderColor=Color(0,0,0,0)
				)
		c.showPage()
		c.save()



# MARK: Main
def main():

	bingoCard = BingoCard()


	bingoCard.genBatchOfCards()

	print("Press Enter to close: ")
	input()


	

if __name__ == '__main__':
	main()