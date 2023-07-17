# BlafKing's .var Merge Tool

This is a custom python script I wrote that merges multiple .var files into a single .var package.

Each .var file contains a meta.json file which needs to define all the content and dependencies that belong to the package.  
This script combines all the meta.json files into a single file and copies all the files & folders from the selected .var packages into one without causing any duplicates!


## How to use

This script can be used both as a packaged .exe or as a python script.  
(The exe file is simply the python script packaged into an .exe using pyinstaller)

### Exe:

1. Download the latest BMT.exe from [Releases](https://github.com/BlafKing/BMT/releases/latest)
2. Once the download is finished, Open up BMT.exe
3. Select the files you want to merge
4. Select a save location
5. Click 'Merge Files'  

NOTE: Using the option to set the dependencies to .latest is incompatible with some packages!  
Please turn it off if you're experiencing issues.

### Python:
1. Make sure [Python](https://www.python.org/downloads/) is installed (I used Python 3.11)
2. Install the required library 'demjson3' with `pip install demjson3`
3. Download the latest Source Code (.zip) from [Releases](https://github.com/BlafKing/BMT/releases/latest)
4. Once the download is finished, extract the contents of the ZIP file to your desired location.
5. Open up BMT.pyw
6. Select the files you want to merge
7. Select a save location  
8. Click 'Merge Files'  

NOTE: Using the option to set the dependencies to .latest is incompatible with some packages!  
Please turn it off if you're experiencing issues.
