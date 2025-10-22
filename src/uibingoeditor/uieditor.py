from tkinter import *
from tkinter import ttk

from PIL import ImageTk, ImageOps

from bingocardmaker import bingocard

root = Tk()

root.title("Bingocard Config Editor")

card = bingocard.BingoCard(quiet=True)
pool = card.loadpool()
cardim = card.createCard(pool)
tim = ImageTk.PhotoImage(ImageOps.contain(cardim, (750,650)))

entryFrame = ttk.Frame(root, height=800, width=700)
entryFrame.grid(column=0, row=0)

cardFrame = ttk.Frame(root, height=800, width=700)
cardFrame.grid(column=1, row=0)


def update_image() -> None:
	cardim = card.createCard(pool)
	tim = ImageTk.PhotoImage(ImageOps.contain(cardim, (750,650)))
	cardImagePanel = ttk.Label(cardFrame, image=tim)
	cardImagePanel.image = tim
	cardImagePanel.grid(column=0, row=0)

# use base image check box
useBaseImageState = IntVar()

def on_toggle_useBaseImage():
	if useBaseImageState.get() == 1:
		card.useBaseImage = True
	else:
		card.useBaseImage = False
	update_image()

cbUserBaseImage = Checkbutton(entryFrame, text="Use Base Image", variable=useBaseImageState, command=on_toggle_useBaseImage)
cbUserBaseImage.grid(row=0, sticky=W)
if card.useBaseImage:
	cbUserBaseImage.select()

# has free space check box
hasFreespaceState = IntVar()

def on_toggle_hasFreespace():
	if hasFreespaceState.get() == 1:
		card.hasFreespace = True
	else:
		card.hasFreespace = False
	update_image()

cbhasFreespace = Checkbutton(entryFrame, text="Has Free Space", variable=hasFreespaceState, command=on_toggle_hasFreespace)
cbhasFreespace.grid(row=1, sticky=W)
if card.hasFreespace:
	cbhasFreespace.select()


update_image()
ttk.Label(cardFrame, image=tim).grid(column=0, row=0)
ttk.Button(cardFrame, text="Reload", command=update_image).grid(column=0, row=1)
root.mainloop()