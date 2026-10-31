import asyncio, json, pathlib, subprocess, edge_tts
root = next(pathlib.Path('G:/').rglob('S1_SUN_ONE_AON'))
spec_p = root / '01_design_spec' / 'S1_EP01_spec.json'
spec = json.loads(spec_p.read_text(encoding='utf-8'))
out_dir = root / '03_audio_master'
out_dir.mkdir(exist_ok=True)
async def gen():
    parts = []
    t_cur = 0.0
    for sc in spec['scenes']:
        mp3 = out_dir / f"sc_{sc['scene_no']}.mp3"
        await edge_tts.Communicate(sc['narration'], spec['voice'], rate=spec['voice_rate']).save(str(mp3))
        r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(mp3)], capture_output=True, text=True)

        dur = round(float(r.stdout.strip()), 2)

        sc['start_sec'] = round(t_cur, 2); sc['duration_sec'] = dur; sc['end_sec'] = round(t_cur + dur, 2); t_cur += dur

        parts.append(str(mp3))

    concat_txt = out_dir / 'concat.txt'

    concat_txt.write_text('\n'.join([f"file '{p.replace(chr(92), '/')}'" for p in parts]), encoding='utf-8')

    voice_all = out_dir / 'voice_all.mp3'

    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat_txt),'-c','copy',str(voice_all)], capture_output=True)

    master_m4a = out_dir / 'S1_EP01_master_audio.m4a'

    flt = f"[0:a]volume=2.0[v];[1:a]volume=0.14,afade=t=in:st=0:d=1.2,afade=t=out:st={max(0, t_cur-1.5)}:d=1.5[b];[v][b]amix=inputs=2:duration=first:dropout_transition=2[a]"

    subprocess.run(['ffmpeg','-y','-i',str(voice_all),'-stream_loop','-1','-i',spec['bgm_path'],'-filter_complex',flt,'-map','[a]','-c:a','aac','-b:a','192k',str(master_m4a)], capture_output=True)

    spec['total_duration_sec'] = round(t_cur, 2); spec['master_audio_path'] = str(master_m4a)

    spec_p.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')

    print('WORKSHOP_03_AUDIO_COMPLETE ->', master_m4a, '| TOTAL_SEC:', round(t_cur, 2), '| SCENE_DURS:', [s['duration_sec'] for s in spec['scenes']])

asyncio.run(gen())
