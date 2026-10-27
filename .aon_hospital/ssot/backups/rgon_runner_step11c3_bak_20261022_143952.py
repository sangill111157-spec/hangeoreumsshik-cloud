import glob,os,ctypes,subprocess
f=sorted(glob.glob(chr(39)+'omni_*.py'[1:]) if 0 else glob.glob('omni_*.py')+glob.glob(os.path.expanduser('~/Downloads/omni_*.py')),key=os.path.getmtime)[-1]
t=open(f,encoding='utf-8').read().replace('Copy','').strip()
open('s_run.py','w',encoding='utf-8').write(t+'\n')
if ctypes.windll.user32.MessageBoxW(0,os.path.basename(f),'RGON RUN',0x40024)==6: subprocess.run(['python','-X','utf8','s_run.py'])
