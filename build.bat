@echo off
pip install -r requirements.txt
pip install pyinstaller

python "build_utils/get_sc2reader_path.py" > sc2reader
SET /p sc2readerpath=<sc2reader
DEL sc2reader

pyinstaller --onefile --clean --windowed --noconfirm --name="SC2ReplayRenamer" --add-data="%sc2readerpath%;sc2reader" --add-data="src;src" run.py