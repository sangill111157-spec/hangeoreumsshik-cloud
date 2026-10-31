const task = await taskSpace("S1 Triumvirate Council"); const p1 = task.page("p1"); await p1.goto("https://www.genspark.ai/agents?type=moa_chat"); console.log(await p1.snapshot());
