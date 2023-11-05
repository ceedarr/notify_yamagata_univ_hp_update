@echo off
chcp 65001 > nul
call C:\Users\Public\env311\Scripts\activate.bat
cd /d %~dp0
python yamagata_univ_hp_notify_1.1.py
echo:
echo 全ての処理が完了しました。ウィンドウを閉じるにはEnterを押してください。
pause > nul
