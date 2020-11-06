# JBG060 User Guide

Tested python version: 3.8
1.	Clone the repository from: https://github.com/dikvangenuchten/JBG060
2.	Create a venv: https://docs.python.org/3/library/venv.html
3.	Run: pip install -f requirements.txt
This will install all the correct version of the packages used.
4.	Add source root to pythonpath
5.	Put the four zipped folders inside …/source_root/data
6.	Run: python main.py \
This will run: \
    1.	The preprocessing steps needed\
    2.	The simulation and train the needed models\
    3.	The visualization present in the poster
      
To run a simulation of how the current system works set dumb in main.py to true

Useful functions/folders that can be ripped out to get a head start:
Preprocessing: Unzipify.py automatically unzips all folders
digital_twin: A low key simulation of the sewage system, can keep track of the internal 
volume of water when testing your own models, and writes a summary to file every step.
