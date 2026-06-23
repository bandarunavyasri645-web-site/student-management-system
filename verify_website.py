import os
import asyncio
from playwright.async_api import async_playwright

async def verify_website():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Load the index.html file
        file_path = f"file://{os.path.abspath('index.html')}"
        await page.goto(file_path)

        print("Adding John Doe...")
        # 1. Add a student
        await page.fill('#name', 'John Doe')
        await page.fill('#roll', '101')

        # Handle alert when adding
        page.once("dialog", lambda dialog: dialog.dismiss())
        await page.click('button:has-text("Add Student")')

        # 2. Verify student is in list
        assert await page.is_visible('td:has-text("John Doe")')
        assert await page.is_visible('td:has-text("101")')

        print("Adding Jane Smith...")
        # 3. Add another student for searching
        await page.fill('#name', 'Jane Smith')
        await page.fill('#roll', '102')
        page.once("dialog", lambda dialog: dialog.dismiss())
        await page.click('button:has-text("Add Student")')

        print("Testing search...")
        # 4. Search for student
        await page.fill('#search-input', 'Jane')
        await page.wait_for_timeout(500) # Wait for debounce/render
        assert await page.is_visible('td:has-text("Jane Smith")')
        assert not await page.is_visible('td:has-text("John Doe")')

        # Clear search
        await page.fill('#search-input', '')
        await page.wait_for_timeout(500)
        assert await page.is_visible('td:has-text("John Doe")')

        print("Testing update...")
        # 5. Update student
        # Find the row for John Doe and click Edit
        await page.locator('.edit-btn').first.click()
        await page.fill('#update-name', 'John Updated')
        page.once("dialog", lambda dialog: dialog.dismiss())
        await page.click('button:has-text("Update Student")')

        assert await page.is_visible('td:has-text("John Updated")')
        assert not await page.is_visible('td:has-text("John Doe")')

        print("Testing delete...")
        # 6. Delete student
        page.once("dialog", lambda dialog: dialog.accept()) # Accept confirmation
        await page.locator('.delete-btn').first.click()

        await page.wait_for_timeout(500)
        assert not await page.is_visible('td:has-text("John Updated")')
        assert await page.is_visible('td:has-text("Jane Smith")')

        # Take a screenshot
        await page.screenshot(path='screenshot.png')
        print("Verification successful! Screenshot saved as screenshot.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_website())
