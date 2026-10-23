"""Capture screenshots of the built app for the README.

Run after `python build.py`:
    python tools/shoot.py

Writes PNGs into screenshots/ (gitignored). Copy the ones you want to keep
into images/ (tracked) and reference them from README.md.
"""
import asyncio
import os
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "dist", "finger-this", "index.html")
OUT = os.path.join(ROOT, "screenshots")
URL = "file:///" + INDEX.replace(os.sep, "/")


async def shot(page, name):
    await page.wait_for_timeout(800)
    await page.screenshot(path=os.path.join(OUT, name))


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Desktop (900x420)
        page = await browser.new_page(viewport={"width": 900, "height": 420})
        await page.goto(URL)
        await shot(page, "scales.png")

        await page.click("#t-tuner"); await shot(page, "tuner.png")
        await page.click("#t-metro"); await shot(page, "metronome.png")
        await page.click("#t-progress"); await shot(page, "progress.png")
        await page.click("#t-scales"); await page.wait_for_timeout(300)
        await page.click("#aboutBtn"); await shot(page, "about.png")

        # Phone landscape (740x350)
        page2 = await browser.new_page(viewport={"width": 740, "height": 350})
        await page2.goto(URL)
        await shot(page2, "scales-phone.png")

        await browser.close()
    print("screenshots written to", OUT)


if __name__ == "__main__":
    asyncio.run(main())