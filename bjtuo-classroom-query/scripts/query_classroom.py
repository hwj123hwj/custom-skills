#!/usr/bin/env python3
"""
Beijing Jiaotong University Classroom Query Script

This script uses Playwright to query classroom schedules at BJTU.
It supports querying by week, building, room, and time period.
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# ================= 环境变量增强加载 =================
def load_secrets_from_file():
    """递归向上查找 .env 或 secrets.json"""
    import json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        # 尝试 .env
        dotenv_path = os.path.join(current_dir, ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            return True
            
        # 尝试 secrets.json
        secrets_path = os.path.join(current_dir, "secrets.json")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        os.environ[k] = str(v)
                return True
            except Exception:
                pass
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            break
        current_dir = parent_dir
    return False

def get_env_flexible(key_name, default=None):
    """灵活获取环境变量：系统变量 -> Windows 注册表 -> 配置文件"""
    val = os.getenv(key_name)
    if val: return val
    
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                val, _ = winreg.QueryValueEx(key, key_name)
                if val: return val
        except Exception:
            pass
    return default

# 初始化加载
load_secrets_from_file()

# Configuration
ZHIPU_API_KEY = get_env_flexible("ZHIPU_API_KEY", "")
ZHIPU_BASE_URL = get_env_flexible("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
ZHIPU_MODEL = get_env_flexible("ZHIPU_MODEL", "GLM-4V-Flash")
BJTU_USERNAME = get_env_flexible("BJTU_USERNAME", "")
BJTU_PASSWORD = get_env_flexible("BJTU_PASSWORD", "")


def recognize_captcha_sync(captcha_url: str) -> str:
    """
    Recognize captcha using Zhipu AI vision model.
    The captcha is a math calculation problem.
    """
    import requests

    if not ZHIPU_API_KEY:
        raise ValueError("ZHIPU_API_KEY environment variable is not set")

    payload = {
        "model": ZHIPU_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": captcha_url}},
                {"type": "text", "text": "只返回数字计算结果，不要任何其他文字"}
            ]
        }]
    }

    headers = {
        "Authorization": f"Bearer {ZHIPU_API_KEY}",
        "Content-Type": "application/json"
    }

    for attempt in range(3):
        try:
            response = requests.post(
                f"{ZHIPU_BASE_URL}chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"].strip()
            # Extract numbers from result
            import re
            numbers = re.findall(r'\d+', result)
            if numbers:
                return numbers[0]
            return result
        except Exception as e:
            if attempt < 2:
                continue
            raise


async def perform_login(page):
    """Login to BJTU CAS system with AI captcha recognition."""
    print("🔐 Logging in to BJTU CAS...")

    # Navigate to login page
    await page.goto("https://mis.bjtu.edu.cn/home/", wait_until="networkidle")

    # Wait for CAS login page or main page
    await page.wait_for_load_state("networkidle")

    # Check if we're on CAS login page
    if "cas.bjtu.edu.cn" in page.url:
        print("   On CAS login page")
        # Fill in credentials
        await page.fill("input[name='loginname']", BJTU_USERNAME)
        await page.fill("input[name='password']", BJTU_PASSWORD)
    else:
        print(f"   Current URL: {page.url}")
        # Try to find login form
        try:
            await page.fill("input[name='loginname']", BJTU_USERNAME, timeout=3000)
            await page.fill("input[name='password']", BJTU_PASSWORD)
        except:
            # Maybe already logged in
            print("   May already be logged in")
            return

    # Get captcha image and recognize it
    captcha_img = await page.query_selector("img[alt='captcha']")
    if captcha_img:
        captcha_src = await captcha_img.get_attribute("src")

        # Download captcha image
        import base64
        if captcha_src.startswith("data:image"):
            # Data URL
            captcha_url = captcha_src
        else:
            # Regular URL - might need to use page absolute URL
            captcha_url = captcha_src if captcha_src.startswith("http") else f"https://cas.bjtu.edu.cn{captcha_src}"

        print("🤖 Recognizing captcha...")
        captcha_result = recognize_captcha_sync(captcha_url)
        print(f"   Captcha result: {captcha_result}")

        await page.fill("input[name='captcha_1']", captcha_result)

    # Click login button
    await page.click("button[type='submit']")
    await page.wait_for_load_state("networkidle")

    # Wait for navigation - might redirect to MIS or stay on CAS if failed
    await page.wait_for_timeout(3000)

    # Check if login successful
    current_url = page.url
    print(f"   After login, URL: {current_url}")

    if "cas.bjtu.edu.cn" in current_url:
        # Check for error messages
        error_elem = await page.query_selector(".error, .alert, [class*='error'], .invalid-feedback")
        if error_elem:
            error_text = await error_elem.text_content()
            print(f"   Error: {error_text}")

        # Save page for debugging
        html = await page.content()
        with open("/tmp/login_failed.html", "w") as f:
            f.write(html)
        print("   Saved page to /tmp/login_failed.html")

        # Check for form errors
        form_errors = await page.query_selector_all("text=/错误|失败|无效|incorrect/i")
        for err in form_errors:
            print(f"   Form error: {await err.text_content()}")

        raise Exception("Login failed - still on CAS page")

    print("✅ Login successful!")


async def query_classrooms(page, date=None, week=21, period=None, semester=None, building=None, room=None):
    """
    Query classroom schedules.

    Args:
        page: Playwright page object (must be logged into mis.bjtu.edu.cn first)
        date: Date string (optional)
        week: Week number (default: 21)
        period: Time period - '上午', '下午', '晚上', '全天' (optional)
        semester: Semester code like '2025-2026-1-2' (optional)
        building: Building code (integer, optional)
        room: Room number (string, optional)

    Returns:
        List of classroom availability results
    """
    print(f"🔍 Querying classrooms - Week: {week}, Building: {building}, Room: {room}")

    # First, navigate to 32号教务系统 to establish session
    print("   Navigating to 32号教务系统...")
    await page.goto("https://mis.bjtu.edu.cn/module/module/10/", wait_until="networkidle")
    await page.wait_for_timeout(2000)

    # Build query parameters
    query_params = []

    # Use current semester as default
    if semester:
        query_params.append(f"zxjxjhh={semester}")

    if week:
        query_params.append(f"zc={week}")

    if building:
        query_params.append(f"jxlh={building}")

    if room:
        query_params.append(f"jash={room}")

    # Construct URL
    base_url = "https://aa.bjtu.edu.cn/classroomtimeholdresult/room_view/"
    if query_params:
        query_string = "&".join(query_params)
        url = f"{base_url}?{query_string}&submit=+%E6%9F%A5+%E8%AF%A2+"
    else:
        url = base_url

    print(f"   URL: {url}")

    # Navigate to query page
    await page.goto(url, wait_until="networkidle")
    await page.wait_for_timeout(2000)

    # Check if redirected to login
    if "login" in page.url.lower():
        raise Exception(f"Session not shared! Redirected to login page: {page.url}")

    # Wait for table to load
    await page.wait_for_selector("table", timeout=10000)

    # Parse the weekly schedule table
    results = await page.evaluate("""
        () => {
            const table = document.querySelector('table');
            if (!table) return [];

            const rows = Array.from(table.querySelectorAll('tr'));
            if (rows.length < 3) return [];

            const results = [];
            const days = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'];

            // Skip header rows (first 2 rows are headers)
            for (let i = 2; i < rows.length; i++) {
                const row = rows[i];
                const cells = Array.from(row.querySelectorAll('td'));

                if (cells.length === 0) continue;

                // First cell is classroom name
                const classroomName = cells[0].textContent?.trim() || '';
                if (!classroomName) continue;

                // Each classroom has 7 days × 7 periods = 49 cells (after the first cell)
                // But the table structure is complex - each day has 7 period columns
                const scheduleData = [];

                for (let day = 0; day < 7; day++) {
                    const dayPeriods = [];

                    for (let period = 1; period <= 7; period++) {
                        // Calculate cell index: 1 (classroom name) + day * 7 + period - 1
                        const cellIndex = 1 + day * 7 + (period - 1);

                        if (cellIndex < cells.length) {
                            const cell = cells[cellIndex];
                            const bgColor = cell.style.backgroundColor || '';
                            const content = cell.textContent?.trim() || '';

                            // Check if cell is occupied (has color or content)
                            const hasColor = bgColor && bgColor !== 'transparent' && bgColor !== 'white' && bgColor !== '#ffffff' && bgColor !== 'rgb(255, 255, 255)';
                            const hasContent = content && content.trim().length > 0;
                            const isOccupied = hasColor || hasContent;

                            dayPeriods.push({
                                period: period,
                                occupied: isOccupied,
                                content: content,
                                bgColor: bgColor
                            });
                        }
                    }

                    scheduleData.push({
                        day: days[day],
                        periods: dayPeriods
                    });
                }

                results.push({
                    room_name: classroomName,
                    schedule: scheduleData
                });
            }

            return results;
        }
    """)

    # Filter results based on period if specified
    if period and period in ['上午', '下午', '晚上']:
        period_map = {
            '上午': [1, 2, 3, 4],
            '下午': [5, 6, 7],
            '晚上': [8, 9, 10]
        }

        target_periods = period_map.get(period, [])

        for result in results:
            free_periods = []
            for day_data in result['schedule']:
                for period_data in day_data['periods']:
                    if not period_data['occupied'] and period_data['period'] in target_periods:
                        free_periods.append(period_data['period'])

            result['free_periods'] = free_periods
            result['status'] = '✅ 空闲' if free_periods else '🔴 已占用'
    elif period == '全天':
        for result in results:
            free_count = 0
            free_info = []
            for day_data in result['schedule']:
                day_free = [p['period'] for p in day_data['periods'] if not p['occupied']]
                if day_free:
                    free_count += len(day_free)
                    free_info.append(f"{day_data['day']}: {day_free}")
            
            result['free_periods_count'] = free_count
            result['free_info'] = free_info
            result['status'] = f'空闲 {free_count} 个时段' if free_count > 0 else '🔴 已占用'
    else:
        # No period filter - just show basic info
        for result in results:
            free_info = []
            for day_data in result['schedule']:
                day_free = [p['period'] for p in day_data['periods'] if not p['occupied']]
                if day_free:
                    free_info.append(f"{day_data['day']}: {day_free}")
            result['free_info'] = free_info
            result['status'] = '查询成功'

    return results


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Query BJTU classroom schedules")
    parser.add_argument("--week", type=int, default=21, help="Week number (1-31)")
    parser.add_argument("--semester", type=str, help="Semester code (e.g., 2025-2026-1-2)")
    parser.add_argument("--building", type=int, help="Building code")
    parser.add_argument("--room", type=str, help="Room number")
    parser.add_argument("--period", type=str, choices=['上午', '下午', '晚上', '全天'], default='全天', help="Time period")

    args = parser.parse_args()

    # Validate environment variables
    if not BJTU_USERNAME:
        print("❌ Error: BJTU_USERNAME environment variable is not set")
        sys.exit(1)
    if not BJTU_PASSWORD:
        print("❌ Error: BJTU_PASSWORD environment variable is not set")
        sys.exit(1)
    if not ZHIPU_API_KEY:
        print("❌ Error: ZHIPU_API_KEY environment variable is not set")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Login
            await perform_login(page)

            # Query classrooms
            results = await query_classrooms(
                page,
                week=args.week,
                semester=args.semester,
                building=args.building,
                room=args.room,
                period=args.period
            )

            # Print results
            print(f"\n📊 找到 {len(results)} 个符合条件的教室:\n")

            for result in results:
                print(f"📍 {result['room_name']}: {result['status']}")

                if 'free_info' in result and result['free_info']:
                    print(f"   📅 空闲详情:")
                    for info in result['free_info']:
                        print(f"      - {info}")
                elif 'free_periods' in result and result['free_periods']:
                    print(f"   空闲节次: {result['free_periods']}")
                elif 'free_periods_count' in result:
                    print(f"   空闲时段数: {result['free_periods_count']}")

            print(f"\n✅ 查询完成！")

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
