import pathlib, re, subprocess
root=next(pathlib.Path('G:/').rglob('S1_SUN_ONE_AON'))
mp4=root/'04_final_mp4'/'S1_EP01_FINAL_MASTER.mp4'
e=pathlib.Path('C:/Users/sangi/Downloads/shin-agent/.env').read_text(encoding='utf-8',errors='ignore')
t=re.search(r'\d{8,12}:[A-Za-z0-9_-]{30,40}',e).group(0)
c=re.findall(r'\b\d{9,11}\b',e)[-1]
r=subprocess.run(['curl.exe','-sS',f'https://api.telegram.org/bot{t}/sendVideo','-F',f'chat_id={c}','-F',f'video=@{mp4}','-F','caption=[S1 Master #EP01] 9.93MB Genuine Motion + Trot BGM + 2-Line Big Caption'],capture_output=True,text=True)
print('WORKSHOP_05_TG_SENT ->', r.stdout[:180])