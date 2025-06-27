@echo off

python sentence_merging.py

cd generated
python split.py
python tokens.py

cd ..

python copy_file.py

cd ../../.. 
cd GEMINI

python script.py

python csvmake.py
