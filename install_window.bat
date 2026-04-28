@echo off
echo Installing MSME Vernacular Voice Assistant for Windows...
echo.

REM Install basic packages
pip install speechrecognition gTTS playsound langchain-google-genai google-generativeai

echo.
echo For microphone support, you need to install PyAudio:
echo.
echo OPTION 1: Install via pipwin (Recommended):
echo   pip install pipwin
echo   pipwin install pyaudio
echo.
echo OPTION 2: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
echo   Then install: pip install PyAudio‑0.2.14‑cp39‑cp39‑win_amd64.whl
echo.

pause
