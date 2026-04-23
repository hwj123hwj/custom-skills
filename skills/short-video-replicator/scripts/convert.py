#!/usr/bin/env python3
"""
MD to PDF converter for short video analysis reports.
Usage: python convert.py <input.md> [output.pdf]

Engine priority:
  1. pandoc + xelatex (best quality)
  2. fpdf2 + Chinese font (pure Python, Chinese support)
"""

import os
import sys
import shutil
import subprocess
import platform
import re
import warnings
from typing import Optional
warnings.filterwarnings("ignore")
from pathlib import Path


# --- Install hints ---

def install_hint_pandoc() -> str:
    s = platform.system()
    if s == "Darwin":   return "brew install pandoc"
    elif s == "Windows":
        for mgr in ["winget", "choco", "scoop"]:
            if shutil.which(mgr): return f"{mgr} install pandoc"
        return "https://pandoc.org/installing.html"
    else: return "sudo apt-get install pandoc"


def install_hint_xelatex() -> str:
    s = platform.system()
    if s == "Darwin":   return "brew install --cask mactex"
    elif s == "Windows":
        if shutil.which("winget"):  return "winget install MiKTeX.MiKTeX"
        elif shutil.which("choco"): return "choco install miktex"
        return "https://miktex.org/download"
    else: return "sudo apt-get install texlive-xetex"


# --- Engine 1: pandoc + xelatex ---

def convert_pandoc(input_path: Path, output_path: Path) -> bool:
    if not shutil.which("pandoc") or not shutil.which("xelatex"):
        return False
    tex_template = Path(__file__).parent / "template.tex"
    cmd = [
        "pandoc", str(input_path), "-o", str(output_path),
        "--pdf-engine=xelatex", "--toc", "--toc-depth=2",
        "-V", "mainfont=Noto Sans CJK SC",
        "-V", "monofont=DejaVu Sans Mono",
        "-V", "geometry=a4paper", "-V", "geometry=margin=1in",
        "-V", "toc-title=目录", "-V", "linestretch=1.5",
    ]
    if tex_template.exists():
        cmd += ["-H", str(tex_template)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return True
    print(f"pandoc error: {result.stderr.strip()}")
    return False


# --- Engine 2: fpdf2 with Chinese font ---

def find_cn_font() -> Optional[str]:
    """
    查找中文字体。
    注意：优先使用 .ttf 单字体文件，避免 fonttools 处理 .ttc 集合字体时
    因 MERG 表无法子集化而丢弃字形，导致中文全部变成占位符的 bug。
    """
    win_root = os.environ.get("SystemRoot", "C:/Windows")
    candidates = [
        # Windows — .ttf 优先
        f"{win_root}/Fonts/simhei.ttf",    # 黑体
        f"{win_root}/Fonts/simfang.ttf",   # 仿宋
        f"{win_root}/Fonts/simkai.ttf",    # 楷体
        f"{win_root}/Fonts/simsun.ttc",    # 宋体（TTC 但字形集简单，兼容性好）
        f"{win_root}/Fonts/msyh.ttc",      # 微软雅黑（TTC，fonttools 可能丢字形）
        # macOS
        "/Library/Fonts/Arial Unicode MS.ttf",
        str(Path.home() / "Library/Fonts/PingFang.ttc"),
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        # Linux
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def find_cn_bold_font(regular_font: Optional[str] = None) -> Optional[str]:
    """
    查找中文粗体字体（用于加粗渲染）。
    注意：fpdf2 对不同字体文件混合注册为同一 family 的 regular/bold 支持不佳，
    multi_cell() 可能出现 "Not enough horizontal space" 错误。
    因此暂时返回 None，使用字号+颜色模拟粗体。
    """
    return None


def parse_md_lines(text: str) -> list:
    """将 Markdown 解析为结构化行列表，每项为 (type, content)"""
    items = []
    in_table = False
    table_rows = []

    for line in text.split("\n"):
        s = line.rstrip()

        # 表格
        if s.startswith("|"):
            cells = [c.strip() for c in s.split("|") if c.strip()]
            # 跳过分隔行 |---|---|
            if all(re.match(r"^[-:]+$", c) for c in cells):
                continue
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            continue
        else:
            if in_table:
                items.append(("table", table_rows))
                table_rows = []
                in_table = False

        if not s:
            items.append(("blank", ""))
        elif s.startswith("#### "):
            items.append(("h4", s[5:]))
        elif s.startswith("### "):
            items.append(("h3", s[4:]))
        elif s.startswith("## "):
            items.append(("h2", s[3:]))
        elif s.startswith("# "):
            items.append(("h1", s[2:]))
        elif s.startswith("> "):
            items.append(("quote", s[2:]))
        elif s.startswith("---"):
            items.append(("hr", ""))
        elif s.startswith("- ") or s.startswith("* "):
            items.append(("li", s[2:]))
        elif re.match(r"^\d+\.\s", s):
            items.append(("oli", s))
        # → 箭头行：有序列表的子项（建议/预期效果等）
        elif s.strip().startswith("\u2192") or s.strip().startswith("->"):
            items.append(("arrow", s.strip()))
        else:
            items.append(("p", s))

    if in_table and table_rows:
        items.append(("table", table_rows))

    return items


def _render_rich_text(pdf, text: str, font_name: str, font_size: float,
                      width: float, line_height: float,
                      base_color: tuple = (35, 35, 35),
                      bold_color: tuple = (10, 10, 10),
                      has_bold_font: bool = False):
    """
    渲染带有 **粗体** 标记的混合文本。
    无粗体字体时通过加大字号 + 纯黑色模拟。
    """
    raw = text

    # 解析 **bold** 段
    segments = []
    bold_pattern = re.compile(r'\*\*(.*?)\*\*')
    last_end = 0
    for m in bold_pattern.finditer(raw):
        if m.start() > last_end:
            segments.append(("normal", raw[last_end:m.start()]))
        segments.append(("bold", m.group(1)))
        last_end = m.end()
    if last_end < len(raw):
        segments.append(("normal", raw[last_end:]))

    if not segments:
        segments = [("normal", raw)]

    # 如果没有任何粗体段，直接用 multi_cell 整段输出
    has_bold = any(s[0] == "bold" for s in segments)
    if not has_bold:
        cleaned = re.sub(r"`(.*?)`", r"\1", text)
        pdf.set_font(font_name, size=font_size)
        pdf.set_text_color(*base_color)
        pdf.multi_cell(width, line_height, cleaned, new_x="LMARGIN", new_y="NEXT")
        return

    # 有粗体段：逐段 write 输出
    # 临时修改左边距为当前 x，确保 write() 换行后缩进正确
    saved_l_margin = pdf.l_margin
    current_x = pdf.x
    pdf.l_margin = current_x

    for style, seg_text in segments:
        seg_text = re.sub(r"`(.*?)`", r"\1", seg_text)
        if style == "bold":
            if has_bold_font:
                pdf.set_font(font_name, style="B", size=font_size)
            else:
                pdf.set_font(font_name, size=font_size + 1)
            pdf.set_text_color(*bold_color)
        else:
            pdf.set_font(font_name, size=font_size)
            pdf.set_text_color(*base_color)
        pdf.write(line_height, seg_text)

    # 恢复左边距，换到下一行（与 multi_cell new_y=NEXT 行为一致）
    pdf.l_margin = saved_l_margin
    pdf.ln(line_height)


# ============================================================
# 排版参数（集中管理，便于调优）
# ============================================================
# 字号 — 层级递减，视觉差异清晰
FONT_H1 = 18        # 一级标题：报告总标题
FONT_H2 = 14        # 二级标题：大板块（结构化文字稿、三维度分析、口播脚本 x 3 ...）
FONT_H3 = 11.5      # 三级标题：板块内小节（一、开场钩子 / 口播1 | ... ）
FONT_H4 = 10.5      # 四级标题：脚本子项（镜头建议 等）
FONT_BODY = 10.5    # 正文
FONT_TABLE = 8.5    # 表格内容
FONT_NOTE = 9       # 注释/创作说明
FONT_ARROW = 10     # 箭头子项

# 行高
LH = 7              # 正文行高（中文需要 ~1.8 倍字号）
LH_H1 = 10          # H1 行高
LH_H2 = 9           # H2 行高
LH_H3 = 8           # H3 行高
LH_H4 = 7           # H4 行高
LH_SM = 6           # 小字行高
LH_TABLE = 5.5      # 表格行高
LH_NOTE = 5.5       # 注释行高

# 间距
SP_AFTER_H1 = 5     # H1 标题下方间距
SP_AFTER_H2 = 3     # H2 标题下方间距
SP_AFTER_H3 = 2     # H3 标题下方间距
SP_AFTER_H4 = 1.5   # H4 标题下方间距
SP_BEFORE_H2 = 6    # H2 标题上方间距
SP_BEFORE_H3 = 4    # H3 标题上方间距
SP_BEFORE_H4 = 3    # H4 标题上方间距
SP_PARA = 2         # 段落间距
SP_LI = 1.5         # 列表项间距
SP_BLANK = 2        # 空行间距
SP_HR = 6           # 水平线上下间距


def convert_fpdf(input_path: Path, output_path: Path) -> bool:
    try:
        from fpdf import FPDF
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "fpdf2"], check=True)
        result = subprocess.run(
            [sys.executable, __file__, str(input_path), str(output_path), "--fpdf-only"],
            text=True
        )
        return result.returncode == 0

    cn_font = find_cn_font()
    cn_bold_font = find_cn_bold_font(regular_font=cn_font)

    class PDF(FPDF):
        def footer(self):
            self.set_y(-15)
            self.set_font(f_body, size=8)
            self.set_text_color(150)
            self.cell(0, 10, f"- {self.page_no()} -", align="C")

    pdf = PDF(orientation="P", unit="mm", format="A4")
    f_body = "cjk" if cn_font else "Helvetica"
    has_bold_font = False

    if cn_font:
        pdf.add_font("cjk", fname=cn_font)
        if cn_bold_font and cn_bold_font != cn_font:
            try:
                pdf.add_font("cjk", style="B", fname=cn_bold_font)
                has_bold_font = True
            except Exception:
                pass

    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    def clean(s: str) -> str:
        """移除 MD 标记，保留纯文本"""
        s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
        s = re.sub(r"\*(.*?)\*", r"\1", s)
        s = re.sub(r"`(.*?)`", r"\1", s)
        return s

    text = input_path.read_text(encoding="utf-8")
    # 预处理：移除代码块
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # 移除 emoji（仅真正的 emoji 符号）
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0"
        "\U0000FE0F"
        "]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub("", text)
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    items = parse_md_lines(text)

    # --- 标题去重/修复 ---
    # 场景：_structured.md 自带 # H1 标题，拼入 report.md 后出现：
    #   ## 结构化文字稿  (H2 板块标题)
    #   # xxx 结构化文字稿 (H1 重复标题)
    # 处理：如果 H2 后面紧跟一个语义相似的 H1，删除那个 H1
    def _clean_duplicate_headings(items):
        cleaned = []
        skip_next = set()
        for i, (typ, content) in enumerate(items):
            if i in skip_next:
                continue
            if typ in ("h1", "h2"):
                # 找到后面的下一个非空元素
                for j in range(i + 1, len(items)):
                    if items[j][0] == "blank":
                        continue
                    next_typ, next_content = items[j]
                    # 如果是同级或更高级标题，且内容相似（包含相同关键词）
                    if next_typ in ("h1", "h2"):
                        t1 = re.sub(r"[\d\-_\s]+", "", clean(content))
                        t2 = re.sub(r"[\d\-_\s]+", "", clean(next_content))
                        if t1 and t2 and (t1 in t2 or t2 in t1):
                            # 保留较短的那个（通常是板块标题），跳过较长的
                            skip_next.add(j)
                            # 同时跳过中间的空行
                            for k in range(i + 1, j):
                                if items[k][0] == "blank":
                                    skip_next.add(k)
                    break
            cleaned.append((typ, content))
        return cleaned

    items = _clean_duplicate_headings(items)

    last_typ = None

    def _next_nonblank_type(idx):
        """从 idx+1 开始找到下一个非空行的类型"""
        for j in range(idx + 1, len(items)):
            if items[j][0] != "blank":
                return items[j][0]
        return None

    for item_idx, (typ, content) in enumerate(items):

        if typ == "blank":
            if last_typ not in ("blank", "h1", "h2", "h3", "h4", "hr"):
                pdf.ln(SP_BLANK)
            last_typ = typ
            continue

        elif typ == "h1":
            # 孤行保护
            if pdf.get_y() > 250:
                pdf.add_page()
            elif pdf.get_y() > 30:
                pdf.ln(8)
            pdf.set_font(f_body, size=FONT_H1)
            pdf.set_text_color(15, 15, 15)
            pdf.multi_cell(0, LH_H1, clean(content), new_x="LMARGIN", new_y="NEXT")
            y = pdf.get_y() + 1.5
            pdf.set_draw_color(30, 30, 30)
            pdf.set_line_width(0.8)
            pdf.line(20, y, 190, y)
            pdf.ln(SP_AFTER_H1)
            last_typ = typ

        elif typ == "h2":
            # 孤行保护
            if pdf.get_y() > 245:
                pdf.add_page()
            pdf.ln(SP_BEFORE_H2)
            pdf.set_font(f_body, size=FONT_H2)
            pdf.set_text_color(25, 45, 130)
            pdf.multi_cell(0, LH_H2, clean(content), new_x="LMARGIN", new_y="NEXT")
            y = pdf.get_y() + 1
            pdf.set_draw_color(80, 110, 195)
            pdf.set_line_width(0.35)
            pdf.line(20, y, 190, y)
            pdf.ln(SP_AFTER_H2)
            last_typ = typ

        elif typ == "h3":
            # 孤行保护
            if pdf.get_y() > 252:
                pdf.add_page()
            pdf.ln(SP_BEFORE_H3)
            pdf.set_font(f_body, size=FONT_H3)
            pdf.set_text_color(40, 40, 90)
            pdf.multi_cell(0, LH_H3, clean(content), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(SP_AFTER_H3)
            last_typ = typ

        elif typ == "h4":
            # 孤行保护
            if pdf.get_y() > 255:
                pdf.add_page()
            pdf.ln(SP_BEFORE_H4)
            pdf.set_font(f_body, size=FONT_H4)
            pdf.set_text_color(70, 70, 100)
            pdf.multi_cell(0, LH_H4, clean(content), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(SP_AFTER_H4)
            last_typ = typ

        elif typ == "quote":
            pdf.ln(2)
            pdf.set_font(f_body, size=FONT_BODY)
            pdf.set_text_color(60, 60, 85)
            pdf.set_fill_color(243, 245, 252)
            pdf.set_draw_color(100, 130, 210)
            pdf.set_line_width(0.8)
            y_start = pdf.get_y()
            pdf.set_x(28)
            pdf.multi_cell(162, LH_SM, clean(content),
                           fill=True, new_x="LMARGIN", new_y="NEXT")
            y_end = pdf.get_y()
            pdf.line(23, y_start, 23, y_end)
            pdf.ln(2)
            last_typ = typ

        elif typ == "hr":
            next_typ = _next_nonblank_type(item_idx)
            if next_typ in ("h1", "h2", "h3", "h4"):
                # 后面紧跟标题——标题本身已有视觉分隔，跳过画线，仅加少量间距
                pdf.ln(3)
            else:
                # 内容块之间的分隔线
                pdf.ln(SP_HR)
                pdf.set_draw_color(160, 165, 180)
                pdf.set_line_width(0.4)
                y = pdf.get_y()
                mid = 105
                pdf.line(mid - 35, y, mid + 35, y)
                pdf.ln(SP_HR)
            last_typ = typ

        elif typ == "li":
            s = clean(content).strip()
            if not s:
                last_typ = typ
                continue
            pdf.set_font(f_body, size=FONT_BODY)
            pdf.set_text_color(25, 25, 25)
            y0 = pdf.get_y()
            pdf.set_xy(27, y0)
            _render_rich_text(pdf, content, f_body, FONT_BODY, 163, LH,
                              base_color=(25, 25, 25), bold_color=(0, 0, 0),
                              has_bold_font=has_bold_font)
            # 圆点
            pdf.set_fill_color(60, 60, 60)
            pdf.ellipse(22, y0 + 2.5, 1.5, 1.5, style="F")
            pdf.ln(SP_LI)
            last_typ = typ

        elif typ == "oli":
            m = re.match(r"^(\d+)\.\s+(.*)", content)
            if m:
                num = m.group(1)
                text_content = m.group(2)
            else:
                num = ""
                text_content = content
            s = clean(text_content).strip()
            if not s and not num:
                last_typ = typ
                continue
            pdf.set_font(f_body, size=FONT_BODY)
            pdf.set_text_color(25, 25, 25)
            y0 = pdf.get_y()
            # 编号
            pdf.set_xy(21, y0)
            pdf.cell(6, LH, f"{num}.", align="R")
            pdf.set_xy(28, y0)
            _render_rich_text(pdf, text_content, f_body, FONT_BODY, 162, LH,
                              base_color=(25, 25, 25), bold_color=(0, 0, 0),
                              has_bold_font=has_bold_font)
            pdf.ln(SP_LI)
            last_typ = typ

        elif typ == "arrow":
            # → 箭头子项：有序列表的建议/预期效果等，缩进显示
            s = clean(content)
            pdf.set_font(f_body, size=FONT_ARROW)
            pdf.set_text_color(50, 80, 140)
            y0 = pdf.get_y()
            pdf.set_xy(32, y0)
            pdf.multi_cell(158, LH_SM, s, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            last_typ = typ

        elif typ == "p":
            s = clean(content)
            if not s.strip():
                last_typ = typ
                continue

            # 检测特殊语义行
            stripped = content.strip()

            # 【】场景标记：蓝色加深
            if re.match(r"^【.*?】", stripped):
                pdf.set_font(f_body, size=FONT_BODY)
                pdf.set_text_color(25, 45, 130)
                pdf.multi_cell(0, LH, s, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(SP_PARA)
                last_typ = typ
                continue

            # （主播出镜）等舞台指示：小字灰色
            if re.match(r"^[\uff08\(].+[\uff09\)]$", stripped):
                pdf.set_font(f_body, size=FONT_NOTE)
                pdf.set_text_color(120, 120, 130)
                pdf.multi_cell(0, LH_NOTE, s, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
                last_typ = typ
                continue

            # 创作说明：小字灰色，带左侧色条
            if stripped.startswith("创作说明") or stripped.startswith("二创说明"):
                pdf.ln(2)
                pdf.set_font(f_body, size=FONT_NOTE)
                pdf.set_text_color(90, 90, 100)
                pdf.set_fill_color(248, 248, 252)
                pdf.set_draw_color(160, 170, 200)
                pdf.set_line_width(0.6)
                y_start = pdf.get_y()
                pdf.set_x(25)
                pdf.multi_cell(165, LH_NOTE, s,
                               fill=True, new_x="LMARGIN", new_y="NEXT")
                y_end = pdf.get_y()
                pdf.line(22, y_start, 22, y_end)
                pdf.ln(2)
                last_typ = typ
                continue

            # 普通段落：富文本渲染
            _render_rich_text(pdf, content, f_body, FONT_BODY, 0, LH,
                              base_color=(30, 30, 30), bold_color=(0, 0, 0),
                              has_bold_font=has_bold_font)
            pdf.ln(SP_PARA)
            last_typ = typ

        elif typ == "table":
            rows = content
            if not rows:
                continue

            pdf.ln(2)
            n_cols = max(len(r) for r in rows)
            page_w = 170
            line_h = LH_TABLE
            font_size = FONT_TABLE

            # 用实际渲染宽度计算列宽（比字符数更精确）
            def calc_col_widths(rows, n_cols, total_w):
                pdf.set_font(f_body, size=font_size)
                max_widths = []
                for j in range(n_cols):
                    max_w = 0
                    for r in rows:
                        cell_text = clean(r[j]) if j < len(r) else ""
                        w = pdf.get_string_width(cell_text) + 4  # padding
                        if w > max_w:
                            max_w = w
                    max_widths.append(max_w)

                total_natural = sum(max_widths) or 1
                if total_natural <= total_w:
                    # 所有列自然宽度能放下，按比例扩展到总宽
                    scale = total_w / total_natural
                    return [w * scale for w in max_widths]
                else:
                    # 放不下，按比例缩减，但保证最小宽度
                    min_w = max(12, total_w / n_cols * 0.5)
                    widths = [max(min_w, total_w * w / total_natural) for w in max_widths]
                    scale = total_w / sum(widths)
                    return [w * scale for w in widths]

            col_widths = calc_col_widths(rows, n_cols, page_w)

            for i, row in enumerate(rows):
                is_header = (i == 0)
                pdf.set_font(f_body, size=font_size)

                # 精确计算每列行数
                cell_lines = []
                for j in range(n_cols):
                    cell_text = clean(row[j]) if j < len(row) else ""
                    cw = col_widths[j] - 3
                    lines = 1
                    cur_w = 0
                    for ch in cell_text:
                        ch_w = pdf.get_string_width(ch)
                        if cur_w + ch_w > cw:
                            lines += 1
                            cur_w = ch_w
                        else:
                            cur_w += ch_w
                    cell_lines.append(lines)

                row_h = max(cell_lines) * line_h + 2

                if pdf.get_y() + row_h > 270:
                    pdf.add_page()

                y_start = pdf.get_y()

                for j in range(n_cols):
                    cell_text = clean(row[j]) if j < len(row) else ""
                    cw = col_widths[j]
                    x_pos = 20 + sum(col_widths[:j])

                    if is_header:
                        pdf.set_fill_color(215, 225, 245)
                        pdf.set_text_color(15, 15, 70)
                    elif i % 2 == 1:
                        pdf.set_fill_color(247, 248, 252)
                        pdf.set_text_color(0)
                    else:
                        pdf.set_fill_color(255, 255, 255)
                        pdf.set_text_color(0)

                    pdf.set_draw_color(195, 200, 215)
                    pdf.set_line_width(0.2)
                    pdf.rect(x_pos, y_start, cw, row_h, style="FD")
                    pdf.set_xy(x_pos + 1.5, y_start + 1)
                    pdf.multi_cell(cw - 3, line_h, cell_text, border=0,
                                   new_x="LMARGIN", new_y="NEXT", max_line_height=line_h)

                pdf.set_y(y_start + row_h)

            pdf.ln(3)
            last_typ = typ

    pdf.output(str(output_path))
    return True


# --- Main ---

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert.py <input.md> [output.pdf]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    args = [a for a in sys.argv[2:] if not a.startswith("--")]
    output_path = Path(args[0]) if args else input_path.with_suffix(".pdf")
    fpdf_only = "--fpdf-only" in sys.argv or "--weasyprint-only" in sys.argv

    if not fpdf_only:
        if shutil.which("pandoc") and shutil.which("xelatex"):
            print("Using pandoc + xelatex...")
            if convert_pandoc(input_path, output_path):
                print(f"PDF saved: {output_path}")
                return
        else:
            print("pandoc/xelatex not found, using fpdf2...")
            if not shutil.which("pandoc"):
                print(f"  To install pandoc: {install_hint_pandoc()}")
            if not shutil.which("xelatex"):
                print(f"  To install xelatex: {install_hint_xelatex()}")

    print("Using fpdf2...")
    try:
        if convert_fpdf(input_path, output_path):
            print(f"PDF saved: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
