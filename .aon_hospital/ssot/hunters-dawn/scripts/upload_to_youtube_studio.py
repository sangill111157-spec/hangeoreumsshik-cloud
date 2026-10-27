import asyncio
import os
from playwright.async_api import async_playwright

VIDEO_PATH = r"C:\Users\sangi\Downloads\Hunters_Dawn_Official_MV.mp4"
THUMBNAIL_PATH = r"C:\Users\sangi\Downloads\Hunters_Dawn_Thumbnail.jpg"
CHANNEL_URL = "https://studio.youtube.com/channel/UCMJn01WLs9ooIhh5x0eJeHg"

TITLE_TEXT = "사냥꾼의 새벽 (Hunter's Dawn) - Official AI Music Video | 어쿠스틱 포크팝"

DESCRIPTION_TEXT = """사냥꾼의 새벽 (Hunter's Dawn) - Official AI Music Video

[수노 오리지널 가사 (Suno Original Lyrics)]
(Intro - Whistling & Cold Wind)

[Verse 1]
심장을 파고드는 Cold shadows in the night
도망쳐봐도 끈질긴 Demons in my mind
"난 안 될 거야"라는 The lies they keep on telling
내 영혼을 갉아먹는 The darkness they’re compelling
But I draw my sword, 이 침묵을 베어내
No more falling back, 이제는 깨어나야 해

[Pre-Chorus]
가장 깊은 어둠은 The darkest hour before dawn
포기하지 마, Your spirit’s not yet gone
차가운 빗줄기는 The armor for your soul
너를 더 단단하게 해, To make you finally whole

[Chorus]
Rise up, Hunter! 넌 무너지지 않아
내 안의 빛으로 Break the chains of the dark
너라는 기적은 The only reason I survive
살아가야 할 이유, You keep my heart alive
You are the one, 세상을 밝힐 유일한 존재
절망을 사냥해, Until the light remains for me and you

[Verse 2]
Abundance is a choice, 풍요는 나의 결단
부정의 마인드란 The monster’s last resistance
비난보다는 확신을, Action over fear
승리의 함성이 The victory is near
내 생각의 크기가 The map of my domain
Hunting down the sorrow, washing off the pain

[Bridge]
상처 입은 영혼이여, Trust the diamond in your chest
지친 너의 어깨 위로 Sunshine will do the rest
너의 존재 자체가 A sacred masterpiece
어둠을 뚫고 나와, Find your inner peace!

[Chorus]
Rise up, Hunter! 넌 무너지지 않아
내 안의 빛으로 Break the chains of the dark
너라는 기적은 The only reason I survive
살아가야 할 이유, You keep my heart alive
You are the one, 세상을 밝힐 유일한 존재
절망을 사냥해, Until the light remains for me and you

[Outro]
I am the hunter, I am the light.
감사함으로 깨운 아침, The demons take flight.
이제 빛의 길로, Together we walk.
Into the dawn.

#사냥꾼의새벽 #HuntersDawn #AIMusicVideo #SunoAI #어쿠스틱포크팝 #AcousticFolkPop #힐링음악 #BreakTheChains"""

async def run():
    async with async_playwright() as p:
        try:
            # Try connecting to existing debug browser
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Connected to existing Chrome CDP instance!")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
        except Exception as e:
            print("Could not connect to CDP, opening new browser instance:", e)
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

        print("Navigating to YouTube Studio...")
        await page.goto(CHANNEL_URL)
        await page.wait_for_timeout(3000)

        # Click Create button
        print("Clicking Create button...")
        create_btn = page.locator("#create-icon")
        if await create_btn.is_visible():
            await create_btn.click()
        else:
            await page.click("ytcp-button#create-icon")

        await page.wait_for_timeout(1000)

        # Click Upload Video
        print("Clicking Upload Video menu...")
        async with page.expect_file_chooser() as fc_info:
            await page.click("tp-yt-paper-item#text-item-0")
        
        file_chooser = await fc_info.value
        print(f"Setting file: {VIDEO_PATH}")
        await file_chooser.set_files(VIDEO_PATH)

        print("Waiting for video upload dialog to initialize...")
        await page.wait_for_timeout(5000)

        # Fill Title
        print("Filling Title...")
        title_input = page.locator("#title-textarea #textbox")
        await title_input.fill(TITLE_TEXT)

        # Fill Description
        print("Filling Description...")
        desc_input = page.locator("#description-textarea #textbox")
        await desc_input.fill(DESCRIPTION_TEXT)

        # Set Thumbnail if available
        print("Setting Thumbnail...")
        async with page.expect_file_chooser() as fc_thumb:
            thumb_btn = page.locator("#file-loader")
            if await thumb_btn.is_visible():
                await thumb_btn.click()
            else:
                await page.click("ytcp-button#select-button")
        file_chooser_thumb = await fc_thumb.value
        await file_chooser_thumb.set_files(THUMBNAIL_PATH)

        # Select Not Made for Kids
        print("Selecting Audience option...")
        await page.click('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]')

        # Open Show More for Language settings
        print("Opening More options for language...")
        more_btn = page.locator("#toggle-button")
        if await more_btn.is_visible():
            await more_btn.click()

        await page.wait_for_timeout(1000)

        # Set Video Language: Korean
        # Set Title and Description Language: Korean

        # Navigate Next -> Next -> Next -> Visibility
        print("Clicking Next to Visibility...")
        for i in range(3):
            await page.click("#next-button")
            await page.wait_for_timeout(1500)

        # Schedule tab
        print("Setting Schedule...")
        await page.click("#second-container-for-account-entry #radio-button")
        
        # Date & Time picker
        # Date: 2026-08-07, Time: 16:45
        date_input = page.locator("#datepicker-trigger input")
        if await date_input.is_visible():
            await date_input.fill("2026. 8. 7.")
        
        time_input = page.locator("#time-of-day-trigger input")
        if await time_input.is_visible():
            await time_input.fill("16:45")

        # Click Schedule Button
        print("Clicking Schedule button...")
        await page.click("#done-button")

        print("Upload and Schedule successfully triggered!")
        await page.wait_for_timeout(5000)

if __name__ == '__main__':
    asyncio.run(run())
