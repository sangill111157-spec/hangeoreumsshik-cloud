Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\sangi\Downloads\shin-agent"
WshShell.Run "pythonw.exe ""C:\Users\sangi\Downloads\shin-agent\rgon_bridge_8765.py""", 0, False
