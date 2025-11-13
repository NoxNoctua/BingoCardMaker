import json
import os
import random
from collections import namedtuple

import logging

from PIL import Image, ImageOps, ImageDraw
import qrcode

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import Color

from logger.logger import Logger


# MARK: Setting up logging

class CustomFormatter(logging.Formatter):
	grey = '\x1b[38;21m'
	blue = '\x1b[38;5;39m'
	yellow = '\x1b[38;5;226m'
	red = '\x1b[38;5;196m'
	bold_red = '\x1b[31;1m'
	reset = '\x1b[0m'

	def __init__(self, fmt):
		super().__init__()
		self.fmt = fmt
		self.FORMATS = {
			logging.DEBUG: self.grey + self.fmt + self.reset,
			logging.INFO: self.blue + self.fmt + self.reset,
			logging.WARNING: self.yellow + self.fmt + self.reset,
			logging.ERROR: self.red + self.fmt + self.reset,
			logging.CRITICAL: self.bold_red + self.fmt + self.reset,
		}
	
	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)

lib_log_root = logging.getLogger("bingocardmaker")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

log = logging.getLogger(__name__)


formatter = CustomFormatter(
	fmt="%(levelname)s:\t %(name)s %(message)s"
)
console_handler.setFormatter(formatter)

lib_log_root.addHandler(console_handler)
lib_log_root.setLevel(logging.DEBUG)


logger = Logger()

# TODO make main that runs the comandline command
# TODO add arguments so that quiet, batchsize, path, log etc can be spcified
# TODO add pause after running
# TODO build to exe
# TODO add to portfolio

class BingoCard:
	

	def __init__(
		self,
		configFilePath=os.path.join("resources", "config.json"),
		quiet=False
	):
		print(__name__)
		self.logger: Logger = None
		# MARK: Named Tuples
		self.BoardShape = namedtuple('BoardShape', 'cols rows')
		self.CardSize = namedtuple('CardSize', 'width hight')
		self.CardPadding = namedtuple('CardPadding', 'top right bottom left')
		self.TileSize = namedtuple('TileSize', 'width hight')
		self.Cord = namedtuple('Cord', 'x y')

		# MARK: Defualt Config
		self.configFilePath: str = os.path.join("resources", "config.json")
		self.name: str = "Bingo Card Maker"
		self.description: str = "Config Load failed"
		self.poolDirectoryPath: str = "pool"
		self.poolImageTypes: [str] = ["PNG"]
		self.baseImagePath: str = "base.png"
		self.freespaceImagePath: str = "freespace.png"
		self.outputPath: str = "output"
		self.boardShape: self.BoardShape = self.BoardShape(5,5)
		self.numTiles = self.boardShape.cols * self.boardShape.rows
		self.hasFreespace: bool = True
		self.freespaceIndex: int = 12
		self.cardSize: self.CardSize = self.CardSize(1000,1000)
		self.cardPadding: self.CardPadding = self.CardPadding(0,0,100,0)
		self.tileSize: self.TileSize = self.TileSize(50,50)
		self.tileStartCor: self.Cord = self.Cord(50,50)
		self.tilepading: int = 5
		self.useBaseImage: bool = True
		self.numOfCardsInBatch: int = 5
		self.imageFileType: [str] = ["PNG", "PDF"]
		self.bgColor: tuple = (255,255,255,255)
		self.drawBoarder: bool = True
		self.boarderColor: tuple = (0,0,0,255)
		self.boarderWidth: int = 4
		self.drawExtraInfo: bool = True
		self.extraInfo: str = "This is a bingo randomizer card creater made by Nox Noxtua"
		self.drawQRCode: bool = True
		self.qrLink: str = "https://github.com/NoxNoctua/BingoCardMaker"
		self.qrLocation: str = "BOTTOM_RIGHT"
		self.drawWatermark: bool = True
		self.watermarkFilePath: str = "watermark.png"
		
		self.load_config_from_json_file(configFilePath, quiet)

	def load_config_from_json_file(self, path: str, quiet=True):
		# MARK: Load Config
		try:
			log.debug(f"Opening config file {path}")
			self.fp = open(path, "r")
			self.config = json.load(self.fp)
			log.debug("loaded json")
			self.name = self.config["name"]
			self.description = self.config["description"]
			self.poolDirectoryPath = self.config["poolDirectoryPath"]
			self.poolImageTypes = self.config["poolImageTypes"]
			self.baseImagePath = self.config["baseImagePath"]
			self.freespaceImagePath = self.config["freespaceImagePath"]
			self.outputPath = self.config["outputPath"]
			log.debug("Trying to load boardshape")
			self.boardShape = self.BoardShape(
				self.config["boardShape"][0],
				self.config["boardShape"][1]
			)
			log.debug("Loaded boardshape")
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
			self.drawExtraInfo = self.config["drawExtraInfo"]
			self.extraInfo = self.config["extraInfo"]
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
			log.exception("Loading the config failed")
		
		log.info(self.name)
		log.info(self.description)

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
			raise Exception()
		
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
	def saveCard(self, cardimg: Image, name: str, imageType: str) -> str:
		log = logger.addTag("saveCard")
		try:
			outfile = os.path.join(
				self.outputPath, 
				(name + "." + imageType.lower())
				)
			log.inf("Saving card {}".format(outfile))
			if self.imageFileType == "JPEG":
				cardimg = cardimg.convert("RGB")
			cardimg.save(outfile, imageType)
			return outfile
		except Exception as e:
			log.err("Failed to save card")
			log.err(str(e))
			return None

	# Generates a single cards with id given id returns file name
	def genCard(self, id: int=None, pool: []=None, fileType: str="PNG") -> str:
		log = logger
		log.tags.append("genCard")
		log.inf(f"Generating Card {id}")

		if pool is None:
			pool = self.loadpool()
		cardimg = self.createCard(pool, id)

		path = "nopath"
		if fileType=="PDF":
			path = self.saveToPDF(cardimg, "card{}".format(id))
		else:
			path = self.saveCard(cardimg, "card{}".format(id), fileType)
		
		log.inf("Generation Complete")

		log.tags.pop()
		return path

	# generates and saves multiple cards with numbered names
	def genBatchOfCards(self, pool = None, asPDF=False):
		log = logger.addTag("genBatchOfCards")
		log.inf("Starting")

		if pool is None:
			pool = self.loadpool()
		for i in range(self.numOfCardsInBatch):
			for t in self.imageFileType:
				self.genCard(id=i,pool=pool,fileType=t)
		log.inf("Generation Complete")

	# MARK: Converting to interactive pdf
	# Convert image to pdf with checkboxes
	# TODO add try catch checks and logging
	def saveToPDF(self, im: Image, name: str, addCheckboxes: bool=True) -> str:
		
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

		return outfile



# MARK: Main
def main():

	bingoCard = BingoCard()


	bingoCard.genBatchOfCards()

	print("Press Enter to close: ")
	input()


	

if __name__ == '__main__':
	main()