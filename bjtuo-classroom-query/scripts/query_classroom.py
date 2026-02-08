# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "playwright",
#     "openai",
#     "python-dotenv",
#     "beautifulsoup4",
# ]
# ///
import asyncio
import os
import base64
import re
import argparse
import sys
import json
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
from playwright.async_api import async_playwright, expect

# 加载配置
load_dotenv(override=True)
# 尝试加载项目根目录的 .env
root_env = os.path.join(os.path.dirname(__file__), "../../.env")
if os.path.exists(root_env):
    load_dotenv(root_env, override=True)

# 尝试加载全局 secrets.json
secrets_path = os.path.join(os.path.dirname(__file__), "../../secrets.json")
if os.path.exists(secrets_path):
    try:
        with open(secrets_path, 'r', encoding='utf-8') as f:
            secrets = json.load(f)
            for k, v in secrets.items():
                if not os.getenv(k):
                    os.environ[k] = str(v)
    except Exception as e:
        print(f"加载 secrets.json 失败: {e}")

# 初始化 OpenAI 客户端 (智谱 AI)
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
)
MODEL = os.getenv("ZHIPU_MODEL", "glm-4v-flash")
USER = os.getenv("BJTU_USERNAME")
PWD = os.getenv("BJTU_PASSWORD")
STATE_FILE = os.path.join(os.path.dirname(__file__), "../auth_state.json")

async def get_captcha_code(page):
    """使用视觉模型识别验证码并计算结果"""
    try:
        captcha_img = page.locator("img.captcha")
        await captcha_img.wait_for(state="visible")
        img_b64 = base64.b64encode(await captcha_img.screenshot()).decode('utf-8')
        
        print("正在调用视觉模型识别验证码...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "识别图中验证码，如果是数学题请直接给出计算结果数字，不要输出其他内容。"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                ]
            }],
            temperature=0.1
        )
        res = response.choices[0].message.content.strip()
        
        expr = "".join(re.findall(r'[\d\+\-\*\/]', res))
        try:
            result = str(eval(expr)) if any(op in expr for op in "+-*/") else res
            final_code = "".join(re.findall(r'\d+', result))
            return final_code
        except:
            return "".join(re.findall(r'\d+', res))
    except Exception as e:
        print(f"验证码识别失败: {e}")
        return ""

async def select_option_robustly(page, selector, user_value, field_name):
    """健壮地选择下拉框选项"""
    if not user_value:
        return False
        
    try:
        await page.wait_for_selector(selector, state="attached", timeout=10000)
        
        try:
            options = await page.eval_on_selector_all(f"{selector} option", """
                elements => elements.map(e => ({
                    text: e.innerText.trim(),
                    value: e.value
                }))
            """)
        except Exception as e:
            local_data_path = os.path.join(os.path.dirname(__file__), "../data/classroom_options.json")
            if os.path.exists(local_data_path):
                print(f"  [提示] 页面获取选项失败，尝试加载本地数据: {local_data_path}")
                with open(local_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    key = None
                    if 'zxjxjhh' in selector: key = 'semesters'
                    elif 'zc' in selector: key = 'weeks'
                    elif 'jxlh' in selector: key = 'buildings'
                    
                    if key and key in data:
                        options = data[key]
                    else:
                        options = []
            else:
                options = []
        
        matched_value = None
        for opt in options:
            if user_value == opt['text'] or user_value == opt['value']:
                matched_value = opt['value']
                break
        
        if not matched_value:
            for opt in options:
                if user_value in opt['text']:
                    print(f"  [提示] 模糊匹配到 {field_name}: '{opt['text']}'")
                    matched_value = opt['value']
                    break

        if not matched_value:
            user_chars = list(user_value)
            for opt in options:
                opt_text = opt['text']
                it = iter(opt_text)
                if all(c in it for c in user_chars):
                    print(f"  [提示] 模糊匹配(子序列)到 {field_name}: '{opt_text}'")
                    matched_value = opt['value']
                    break
        
        if matched_value:
            try:
                is_visible = await page.is_visible(selector)
                if is_visible:
                    await page.locator(selector).select_option(matched_value)
                else:
                    await page.locator(selector).select_option(matched_value, force=True)
                    has_jquery = await page.evaluate("typeof jQuery !== 'undefined'")
                    if has_jquery:
                        await page.evaluate("""([selector, value]) => {
                            var $select = jQuery(selector);
                            $select.val(value);
                            $select.trigger('chosen:updated');
                            $select.trigger('change');
                        }""", [selector, matched_value])
                    else:
                        await page.dispatch_event(selector, 'change')
            except Exception as e:
                await page.evaluate("""([selector, value]) => {
                    var select = document.querySelector(selector);
                    select.value = value;
                    select.dispatchEvent(new Event('change', { bubbles: true }));
                }""", [selector, matched_value])
            return True
        else:
            print(f"  [错误] 未能找到匹配的 {field_name}: '{user_value}'")
            return False
            
    except Exception as e:
        print(f"  [异常] 选择 {field_name} 时出错: {e}")
        return False

async def run(semester, week, building, classroom, headless=False):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = None
        if os.path.exists(STATE_FILE):
            try:
                context = await browser.new_context(storage_state=STATE_FILE)
            except Exception:
                pass
                
        if not context:
            context = await browser.new_context()
            
        page = await context.new_page()
        print("访问登录页面...")
        await page.goto("https://mis.bjtu.edu.cn/home/")
        
        if "auth/login" in page.url:
            print("执行登录流程...")
            if not USER or not PWD:
                print("错误: 未配置 BJTU_USERNAME 或 BJTU_PASSWORD")
                return
            await page.get_by_placeholder("用户名").fill(USER)
            await page.get_by_placeholder("密码").fill(PWD)
            code = await get_captcha_code(page)
            print(f"识别验证码: {code}")
            await page.locator("#id_captcha_1").fill(code)
            await page.click("button.btn-primary")
            try:
                await page.wait_for_url(re.compile(r"home/"), timeout=15000)
                await context.storage_state(path=STATE_FILE)
            except:
                if "auth/login" in page.url:
                    print("登录失败，请检查验证码或凭据。")
                    await browser.close()
                    return
        else:
            print("已通过缓存状态自动登录。")
        
        print("正在进入教室查询...")
        mis_link = page.get_by_role("link", name="教务系统")
        await mis_link.wait_for(state="visible", timeout=10000)
        async with page.expect_popup() as page1_info:
            await mis_link.click()
        page1 = await page1_info.value
        await page1.wait_for_load_state("networkidle")
        
        try:
            if not await page1.get_by_text("考务成绩").is_visible():
                toggler = page1.locator("#menu-toggler2")
                if await toggler.is_visible():
                    await toggler.click()
                    await asyncio.sleep(1)
        except:
            pass
            
        await page1.get_by_text("考务成绩").click()
        await page1.get_by_role("link", name="教室").click()
        
        await select_option_robustly(page1, "select[name='zxjxjhh']", semester, "学期")
        await select_option_robustly(page1, "select[name='zc']", week, "周次")
        await select_option_robustly(page1, "select[name='jxlh']", building, "楼栋")
        
        if classroom:
            await page1.get_by_role("textbox", name="教室").fill(classroom)
        
        await page1.get_by_role("button", name="查 询").click()
        print("等待结果加载...")
        
        try:
            await page1.wait_for_selector("table", timeout=10000)
            content = await page1.content()
            soup = BeautifulSoup(content, 'html.parser')
            tables = soup.find_all("table")
            target_table = None
            for tbl in tables:
                if "星期一" in tbl.get_text():
                    target_table = tbl
                    break
            
            if target_table:
                rows = target_table.find_all("tr")
                header_cells = rows[1].find_all(["td", "th"])
                slots_per_day = 7
                if len(header_cells) > 1:
                    total_slots = len(header_cells) - 1
                    if total_slots % 7 == 0:
                        slots_per_day = total_slots // 7
                
                data_rows = rows[2:]
                for tr in data_rows:
                    cols = tr.find_all("td")
                    if not cols: continue
                    room_name = cols[0].get_text(strip=True)
                    print(f"\n教室: {room_name}")
                    
                    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                    free_slots = []
                    for i, cell in enumerate(cols[1:]):
                        day_idx = i // slots_per_day
                        period = (i % slots_per_day) + 1
                        if day_idx >= 7: break
                        
                        text = cell.get_text(strip=True)
                        style = cell.get('style', '').lower()
                        bgcolor = cell.get('bgcolor', '').lower()
                        
                        is_free = False
                        bg_color_found = None
                        if 'background-color' in style:
                            match = re.search(r'background-color\s*:\s*([^;]+)', style)
                            if match: bg_color_found = match.group(1).strip()
                        elif bgcolor:
                            bg_color_found = bgcolor
                        
                        if not text:
                            if not bg_color_found or any(c in bg_color_found for c in ['#fff', '#ffffff', 'white', 'transparent']):
                                is_free = True
                        if is_free:
                            free_slots.append(f"{days[day_idx]} 第{period}节")
                    
                    if free_slots:
                        print(f"  空闲时间段: {', '.join(free_slots)}")
                    else:
                        print("  无空闲时间段。")
        except Exception as e:
            print(f"结果解析失败: {e}")
        
        screenshot_path = "classroom_result.png"
        await page1.screenshot(path=screenshot_path)
        print(f"结果截图已保存: {screenshot_path}")
        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BJTU 教室查询")
    parser.add_argument("--semester", help="学期 (2025-2026-1)")
    parser.add_argument("--week", help="周次 (14)")
    parser.add_argument("--building", help="教学楼")
    parser.add_argument("--classroom", help="教室号")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    args = parser.parse_args()
    asyncio.run(run(args.semester, args.week, args.building, args.classroom, args.headless))
