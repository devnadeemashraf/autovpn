"""Test Puppeteer setup for automation."""

import asyncio
from pyppeteer import launch


async def test_puppeteer_setup():
    """Test Puppeteer browser setup."""
    print("🔍 Testing Puppeteer setup...")

    try:
        # Test browser launch
        browser = await launch(
            {
                "headless": True,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--window-size=1920,1080",
                ],
            }
        )

        print("✅ Puppeteer browser launched successfully")

        # Test page creation
        page = await browser.newPage()
        await page.setViewport({"width": 1920, "height": 1080})
        print("✅ Page created successfully")

        # Test navigation
        await page.goto("https://www.google.com")
        print("✅ Navigation successful")

        # Test element interaction
        title = await page.title()
        print(f"✅ Page title: {title}")

        # Clean up
        await browser.close()
        print("✅ Browser closed successfully")

        print("\n🎉 All Puppeteer tests passed!")
        return True

    except Exception as e:
        print(f"❌ Puppeteer test failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("PUPPETEER SETUP TEST")
    print("=" * 50)

    success = asyncio.run(test_puppeteer_setup())

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    if success:
        print("✅ Puppeteer is working correctly!")
        print("✅ Automation should work now.")
    else:
        print("❌ Puppeteer setup failed.")
        print("💡 Try installing pyppeteer: pip install pyppeteer")
