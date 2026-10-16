Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "c:\Users\sangi\Downloads\shin-agent"
' 검은 창 숨김(0) 모드로 배치 실행
WshShell.Run "cmd /c ""c:\Users\sangi\Downloads\shin-agent\한걸음씩_만능_AI_사령부_실행.bat""", 0, False
