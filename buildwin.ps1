& .\.venv\Scripts\activate
pyinstaller --noconfirm --log-level=WARN `
	--onedir --nowindowed `
	--name="BingoMaker_Gen_Batch" `
	--path=".venv" `
	--hidden-import="PIL" `
	--add-data="README.md:." `
	--add-data="SampleBaseImage.png:Sample" `
	--add-data="SampleFreeSpace.png:Sample" `
	--add-data="config.json:Sample" `
	--add-data="LICENSE:." `
	--add-data="pool:Sample\pool" `
	src\bingocardmaker\bingocard.py

Copy-Item "SampleBaseImage.png" -Destination "dist\BingoMaker_Gen_Batch"
Copy-Item "SampleFreeSpace.PNG" -Destination "dist\BingoMaker_Gen_Batch"
Copy-Item "config.json" -Destination "dist\BingoMaker_Gen_Batch"
Copy-Item "pool" -Destination "dist\BingoMaker_Gen_Batch" -Recurse

New-Item -Path "dist\BingoMaker_Gen_Batch\output" -ItemType Directory