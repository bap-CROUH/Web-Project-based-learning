#!/usr/bin/env python3
"""
Convert README.md into rich structured JSON for the localhost GUI.
Categorizes projects by language, subcategory, difficulty, series, and tags.
"""

import json
import re
import os
import sys

# Add scripts directory to path to reuse check_readme classifier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_readme

README_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "data")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "projects.json")

# Language icons and color themes for rich UI
LANG_META = {
    "C/C++": {"icon": "devicon-cplusplus-plain", "color": "#00599C", "badge": "C / C++", "category": "Systems & Low-level"},
    "C#": {"icon": "devicon-csharp-plain", "color": "#239120", "badge": "C# (.NET)", "category": "Enterprise & Games"},
    "Clojure": {"icon": "devicon-clojure-line", "color": "#5881D8", "badge": "Clojure", "category": "Functional"},
    "Dart": {"icon": "devicon-dart-plain", "color": "#0175C2", "badge": "Dart / Flutter", "category": "Mobile & Multi-platform"},
    "Elixir": {"icon": "devicon-elixir-plain", "color": "#4E2A8E", "badge": "Elixir", "category": "Functional & Concurrency"},
    "Erlang": {"icon": "devicon-erlang-plain", "color": "#A90533", "badge": "Erlang", "category": "Distributed Systems"},
    "F#": {"icon": "devicon-fsharp-plain", "color": "#B845FC", "badge": "F#", "category": "Functional"},
    "Go": {"icon": "devicon-go-original-wordmark", "color": "#00ADD8", "badge": "Go (Golang)", "category": "Backend & Cloud"},
    "Haskell": {"icon": "devicon-haskell-plain", "color": "#5E5086", "badge": "Haskell", "category": "Pure Functional"},
    "HTML/CSS": {"icon": "devicon-html5-plain", "color": "#E34F26", "badge": "HTML & CSS", "category": "Frontend Foundations"},
    "HTML and CSS": {"icon": "devicon-html5-plain", "color": "#E34F26", "badge": "HTML & CSS", "category": "Frontend Foundations"},
    "Java": {"icon": "devicon-java-plain", "color": "#ED8B00", "badge": "Java", "category": "Enterprise & Mobile"},
    "JavaScript": {"icon": "devicon-javascript-plain", "color": "#F7DF1E", "badge": "JavaScript", "category": "Fullstack Web"},
    "Kotlin": {"icon": "devicon-kotlin-plain", "color": "#7F52FF", "badge": "Kotlin", "category": "Mobile & JVM"},
    "Lua": {"icon": "devicon-lua-plain", "color": "#000080", "badge": "Lua", "category": "Scripting & Game Dev"},
    "OCaml": {"icon": "devicon-ocaml-plain", "color": "#EE6A1A", "badge": "OCaml", "category": "Functional & Compilers"},
    "PHP": {"icon": "devicon-php-plain", "color": "#777BB4", "badge": "PHP", "category": "Web Backend"},
    "Python": {"icon": "devicon-python-plain", "color": "#3776AB", "badge": "Python", "category": "AI, Data & Backend"},
    "R": {"icon": "devicon-r-plain", "color": "#276DC3", "badge": "R", "category": "Data Science & Stats"},
    "Ruby": {"icon": "devicon-ruby-plain", "color": "#CC342D", "badge": "Ruby", "category": "Web & Scripting"},
    "Rust": {"icon": "devicon-rust-plain", "color": "#DEA584", "badge": "Rust", "category": "Systems & WebAssembly"},
    "Scala": {"icon": "devicon-scala-plain", "color": "#DC322F", "badge": "Scala", "category": "Big Data & JVM"},
    "Swift": {"icon": "devicon-swift-plain", "color": "#FA7343", "badge": "Swift", "category": "iOS & Apple"},
    "Additional Resources": {"icon": "devicon-github-original", "color": "#6e5494", "badge": "Resources", "category": "Learning Resources"},
}

def determine_difficulty(title, parent, cat, subcat, lang, url):
    """
    Evaluates project difficulty from 1 (Easy / Beginner) to 4 (Expert / Low-Level).
    Returns (score, label, vi_label, reason, est_hours).
    """
    text = f"{title} {parent or ''} {cat or ''} {subcat or ''}".lower()
    
    # 4: Chuyên sâu / Rất khó (Expert / Low-level Systems)
    expert_patterns = [
        r'\bkernel\b', r'\bbootloader\b', r'\bcompiler\b', r'\bjit\b', r'\bdebugger\b',
        r'tcp/ip', r'\bos\b from scratch', r'operating system', r'\bemulator\b', r'chip-8',
        r'\binterpreter\b', r'\bllvm\b', r'\bkvm\b', r'container in 500', r'virtual machine',
        r'lc3-vm', r'\blisp\b', r'scheme in 48', r'craftinginterpreters', r'handmade hero',
        r'bytecode runner', r'game boy emulator', r'pure rust', r'nes_ebook', r'write an os'
    ]
    for pat in expert_patterns:
        if re.search(pat, text):
            return {
                "level": 4,
                "label": "Expert",
                "vi_label": "Chuyên sâu",
                "color": "#ef4444", # Red/Rose
                "bg_color": "rgba(239, 68, 68, 0.15)",
                "est_hours": "30 - 80+ giờ",
                "badge_class": "diff-expert"
            }
            
    # 3: Nâng cao (Advanced)
    adv_patterns = [
        r'\bredis\b', r'bittorrent', r'\bmqtt\b', r'raytracing', r'raytracer', r'tiny renderer',
        r'software rendering', r'blockchain', r'search engine', r'text editor', r'hecto', r'kilo',
        r'\byolo\b', r'\bcnn\b', r'deep learning', r'mask-r-cnn', r'segmentation', r'face recognition',
        r'neural net', r'actor-based', r'virtual dom', r'build yourself a redux', r'concurrent server',
        r'roguelike', r'memory allocator', r'fuse filesystem', r'nes game', r'key-value store',
        r'matrix multiplication', r'dlib', r'facial landmark', r'transfer learning', r'pytorch',
        r'tensorflow', r'evolution', r'p2p', r'quora questions', r'fake news', r'malaria',
        r'root health', r'inception', r'captcha'
    ]
    if (cat in ['Deep Learning', 'OpenCV', 'OpenGL', 'Network programming'] or
        any(re.search(pat, text) for pat in adv_patterns)):
        return {
            "level": 3,
            "label": "Advanced",
            "vi_label": "Nâng cao",
            "color": "#f59e0b", # Amber/Orange
            "bg_color": "rgba(245, 158, 11, 0.15)",
            "est_hours": "12 - 25 giờ",
            "badge_class": "diff-advanced"
        }
        
    # 1: Cơ bản / Dễ (Beginner / Easy)
    easy_patterns = [
        r'calculator', r'\btodo\b', r'to-do', r'weather app', r'quote machine', r'flashlight',
        r'loading screen', r'blank app', r'tic-tac-toe', r'wordle', r'simple rpg',
        r'simple http server', r'simple search bot', r'30 things in 30 days', r'streamlit',
        r'line chart', r'ascii art', r'photomosaic', r'simple chat app with elixir',
        r'simple wine', r'fruits classification', r'linear regression', r'smile classifier',
        r'note app', r'beginner', r'getting started'
    ]
    if any(re.search(pat, text) for pat in easy_patterns):
        return {
            "level": 1,
            "label": "Beginner",
            "vi_label": "Cơ bản / Dễ",
            "color": "#10b981", # Emerald green
            "bg_color": "rgba(16, 185, 129, 0.15)",
            "est_hours": "2 - 5 giờ",
            "badge_class": "diff-beginner"
        }

    # 2: Trung bình (Intermediate - standard full-stack, bots, clones, typical web/mobile apps)
    return {
        "level": 2,
        "label": "Intermediate",
        "vi_label": "Trung bình",
        "color": "#06b6d4", # Cyan / Blue
        "bg_color": "rgba(6, 182, 212, 0.15)",
        "est_hours": "6 - 12 giờ",
        "badge_class": "diff-intermediate"
    }

def detect_format(title, tail, url):
    """Detect if resource is a video, article, multi-part series, book, etc."""
    combined = f"{title} {tail} {url}".lower()
    if "(video" in combined or "youtube.com" in combined or "youtu.be" in combined:
        return {"type": "video", "label": "Video", "icon": "fa-play-circle"}
    if "book" in combined or "gitbooks.io" in combined:
        return {"type": "book", "label": "E-Book", "icon": "fa-book"}
    if "github.com" in combined and ("/wiki" in combined or "/issues/" in combined):
        return {"type": "repo-guide", "label": "Guide/Repo", "icon": "fa-code"}
    return {"type": "article", "label": "Bài viết / Lab", "icon": "fa-newspaper"}

def generate_tags(title, parent, cat, subcat, lang):
    tags = set()
    if lang:
        tags.add(lang.replace(":", "").strip())
    if cat:
        tags.add(cat.replace(":", "").strip())
    if subcat:
        tags.add(subcat.replace(":", "").strip())
        
    combined = f"{title} {parent or ''}".lower()
    keywords = {
        "react": "React", "vue": "Vue", "angular": "Angular", "next.js": "Next.js",
        "flutter": "Flutter", "django": "Django", "flask": "Flask", "laravel": "Laravel",
        "docker": "Docker", "graphql": "GraphQL", "websocket": "WebSockets",
        "socket": "Sockets", "redis": "Redis", "mongodb": "MongoDB", "postgres": "PostgreSQL",
        "opencv": "OpenCV", "pytorch": "PyTorch", "tensorflow": "TensorFlow", "keras": "Keras",
        "game": "Game Dev", "crawler": "Scraping", "scrape": "Scraping", "bot": "Bot",
        "compiler": "Compiler", "os": "Operating Systems", "blockchain": "Blockchain",
        "wasm": "WebAssembly", "electron": "Electron", "sdl": "SDL2", "opengl": "OpenGL"
    }
    for k, v in keywords.items():
        if re.search(r'\b' + k + r'\b', combined):
            tags.add(v)
    return sorted(list(tags))

def build_vietnamese_summary(title, parent, cat, subcat, lang, diff_info):
    """Generates an intuitive Vietnamese description of the project."""
    name = parent if parent else title
    lvl = diff_info["vi_label"]
    
    parts = []
    if parent:
        parts.append(f"Chuyên đề học tập trong series **{parent}**.")
    
    if "compiler" in name.lower() or "trình biên dịch" in name.lower():
        parts.append("Hướng dẫn từng bước xây dựng một trình biên dịch hoàn chỉnh: phân tích từ vựng (lexer), cú pháp (parser), tạo mã máy và tối ưu hóa.")
    elif "os" in name.lower() or "kernel" in name.lower() or "bootloader" in name.lower():
        parts.append("Tìm hiểu cấu trúc hệ điều hành, cách nạp kernel, quản lý bộ nhớ, ngắt và lập trình vi điều khiển tầng thấp.")
    elif "emulator" in name.lower():
        parts.append("Tự tay lập trình giả lập phần cứng máy chơi game: giả lập CPU registers, bộ nhớ, opcode và render đồ họa.")
    elif "clone" in name.lower():
        parts.append("Xây dựng bản sao ứng dụng thực tế với đầy đủ kiến trúc frontend/backend, giao diện người dùng và cơ sở dữ liệu.")
    elif "chat" in name.lower() or "websocket" in name.lower():
        parts.append("Lập trình ứng dụng nhắn tin thời gian thực với xử lý đa luồng, sockets và đồng bộ hóa trạng thái.")
    elif "game" in name.lower() or "tetris" in name.lower() or "space invaders" in name.lower():
        parts.append("Phát triển trò chơi từ con số 0: xử lý game loop, va chạm, đồ họa sprites, âm thanh và logic điểm số.")
    elif "bot" in name.lower():
        parts.append("Tạo bot tự động hóa tương tác với API nền tảng, xử lý dữ liệu và phản hồi sự kiện webhook.")
    elif "deep learning" in name.lower() or "neural" in name.lower():
        parts.append("Huấn luyện mô hình mạng nơ-ron nhân tạo với dữ liệu thực tế, tiền xử lý và tối ưu độ chính xác.")
    elif "opencv" in name.lower():
        parts.append("Xử lý ảnh thị giác máy tính: nhận diện khuôn mặt, bóc tách vật thể, phân đoạn hình ảnh và camera stream.")
    elif "blockchain" in name.lower():
        parts.append("Tìm hiểu nguyên lý mật mã học phân tán, cơ chế đồng thuận Proof of Work, chuỗi khối và giao dịch.")
    elif "todo" in name.lower() or "calculator" in name.lower():
        parts.append("Dự án kinh điển để nắm vững cú pháp cốt lõi, tư duy lập trình và quản lý trạng thái cơ bản.")
    else:
        parts.append(f"Dự án thực chiến dựa trên {lang}, hướng dẫn xây dựng sản phẩm từ đầu kèm code mẫu và giải thích chi tiết.")
        
    return " ".join(parts)

def parse_readme_to_projects():
    with open(README_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    current_lang = "General"
    current_cat = ""
    current_subcat = ""
    series_stack = {} # depth -> dict with series info

    flat_entries = []
    
    for idx, raw in enumerate(lines):
        ln = raw.rstrip("\r\n")
        lineno = idx + 1
        if not ln.strip():
            continue
        kind = check_readme.classify_line(ln)
        tag = kind[0]
        
        if tag == "header":
            lvl, title = kind[1], kind[2]
            title_clean = title.rstrip(":").strip()
            if lvl == 2:
                current_lang = title_clean
                current_cat = ""
                current_subcat = ""
                series_stack.clear()
            elif lvl == 3:
                current_cat = title_clean
                current_subcat = ""
                series_stack.clear()
            elif lvl == 4:
                current_subcat = title_clean
                series_stack.clear()
                
        elif tag == "series":
            depth, title = kind[1], kind[2]
            series_stack[depth] = {
                "title": title.strip(),
                "lang": current_lang,
                "cat": current_cat,
                "subcat": current_subcat,
                "line": lineno
            }
            # Remove any deeper series
            for k in list(series_stack.keys()):
                if k > depth:
                    del series_stack[k]
                    
        elif tag == "entry":
            depth, title, url, tail, extra_urls = kind[1], kind[2], kind[3], kind[4], kind[5]
            
            # Find parent series
            parent = None
            parent_series_info = None
            for d in range(depth - 1, -1, -1):
                if d in series_stack:
                    parent_series_info = series_stack[d]
                    parent = parent_series_info["title"]
                    break
                    
            entry_lang = parent_series_info["lang"] if parent_series_info else current_lang
            entry_cat = parent_series_info["cat"] if parent_series_info else current_cat
            entry_subcat = parent_series_info["subcat"] if parent_series_info else current_subcat
            
            # Clean tail notes
            clean_tail = tail.strip()
            
            diff_info = determine_difficulty(title, parent, entry_cat, entry_subcat, entry_lang, url)
            fmt_info = detect_format(title, clean_tail, url)
            tags = generate_tags(title, parent, entry_cat, entry_subcat, entry_lang)
            summary = build_vietnamese_summary(title, parent, entry_cat, entry_subcat, entry_lang, diff_info)
            
            entry_dict = {
                "id": f"pbl-{lineno}",
                "line": lineno,
                "title": title.strip(),
                "url": url.strip(),
                "tail": clean_tail,
                "extra_urls": extra_urls,
                "parent_series": parent,
                "language": entry_lang,
                "category": entry_cat or "Cốt lõi (Core)",
                "subcategory": entry_subcat,
                "difficulty": diff_info["level"],
                "difficulty_label": diff_info["label"],
                "difficulty_vi": diff_info["vi_label"],
                "difficulty_color": diff_info["color"],
                "difficulty_bg": diff_info["bg_color"],
                "badge_class": diff_info["badge_class"],
                "estimated_hours": diff_info["est_hours"],
                "format": fmt_info["type"],
                "format_label": fmt_info["label"],
                "format_icon": fmt_info["icon"],
                "tags": tags,
                "summary_vi": summary,
                "is_http": url.startswith("http://")
            }
            flat_entries.append(entry_dict)

    # Now group entries by parent series when appropriate
    # Grouped projects represent cohesive tutorial units
    grouped_projects = []
    
    # Track which series has been grouped
    grouped_series_map = {}
    
    for item in flat_entries:
        parent = item["parent_series"]
        if not parent:
            # Standalone project
            grouped_projects.append({
                "id": item["id"],
                "title": item["title"],
                "is_series": False,
                "series_count": 1,
                "parts": [{
                    "title": item["title"],
                    "url": item["url"],
                    "tail": item["tail"],
                    "format": item["format_label"],
                    "line": item["line"]
                }],
                "primary_url": item["url"],
                "tail": item["tail"],
                "language": item["language"],
                "category": item["category"],
                "subcategory": item["subcategory"],
                "difficulty": item["difficulty"],
                "difficulty_label": item["difficulty_label"],
                "difficulty_vi": item["difficulty_vi"],
                "difficulty_color": item["difficulty_color"],
                "difficulty_bg": item["difficulty_bg"],
                "badge_class": item["badge_class"],
                "estimated_hours": item["estimated_hours"],
                "format": item["format"],
                "format_label": item["format_label"],
                "format_icon": item["format_icon"],
                "tags": item["tags"],
                "summary_vi": item["summary_vi"],
                "is_http": item["is_http"],
                "line": item["line"]
            })
        else:
            # In a series
            series_key = f"{item['language']}::{item['category']}::{parent}"
            if series_key not in grouped_series_map:
                # First time seeing this series
                # Determine difficulty for whole series (take max difficulty of its items)
                proj = {
                    "id": f"series-{len(grouped_series_map) + 1}",
                    "title": parent,
                    "is_series": True,
                    "series_count": 0,
                    "parts": [],
                    "primary_url": item["url"],
                    "tail": item["tail"],
                    "language": item["language"],
                    "category": item["category"],
                    "subcategory": item["subcategory"],
                    "difficulty": item["difficulty"],
                    "difficulty_label": item["difficulty_label"],
                    "difficulty_vi": item["difficulty_vi"],
                    "difficulty_color": item["difficulty_color"],
                    "difficulty_bg": item["difficulty_bg"],
                    "badge_class": item["badge_class"],
                    "estimated_hours": item["estimated_hours"],
                    "format": item["format"],
                    "format_label": "Series nhiều phần",
                    "format_icon": "fa-layer-group",
                    "tags": item["tags"],
                    "summary_vi": item["summary_vi"],
                    "is_http": item["is_http"],
                    "line": item["line"]
                }
                grouped_series_map[series_key] = proj
                grouped_projects.append(proj)
            
            proj = grouped_series_map[series_key]
            proj["parts"].append({
                "title": item["title"],
                "url": item["url"],
                "tail": item["tail"],
                "format": item["format_label"],
                "line": item["line"]
            })
            proj["series_count"] = len(proj["parts"])
            # Update tags and difficulty
            proj["tags"] = sorted(list(set(proj["tags"] + item["tags"])))
            if item["difficulty"] > proj["difficulty"]:
                proj["difficulty"] = item["difficulty"]
                proj["difficulty_label"] = item["difficulty_label"]
                proj["difficulty_vi"] = item["difficulty_vi"]
                proj["difficulty_color"] = item["difficulty_color"]
                proj["difficulty_bg"] = item["difficulty_bg"]
                proj["badge_class"] = item["badge_class"]
                proj["estimated_hours"] = item["estimated_hours"]

    # Compute statistics
    languages_stats = {}
    for p in grouped_projects:
        lang = p["language"]
        if lang not in languages_stats:
            meta = LANG_META.get(lang, {"icon": "devicon-code-plain", "color": "#6366f1", "badge": lang, "category": "General"})
            languages_stats[lang] = {
                "name": lang,
                "count": 0,
                "parts_count": 0,
                "icon": meta["icon"],
                "color": meta["color"],
                "category": meta["category"],
                "difficulties": {1: 0, 2: 0, 3: 0, 4: 0}
            }
        languages_stats[lang]["count"] += 1
        languages_stats[lang]["parts_count"] += len(p["parts"])
        languages_stats[lang]["difficulties"][p["difficulty"]] += 1

    difficulty_stats = {
        1: {"count": 0, "label": "Cơ bản / Dễ (Beginner)", "color": "#10b981"},
        2: {"count": 0, "label": "Trung bình (Intermediate)", "color": "#06b6d4"},
        3: {"count": 0, "label": "Nâng cao (Advanced)", "color": "#f59e0b"},
        4: {"count": 0, "label": "Chuyên sâu (Expert)", "color": "#ef4444"}
    }
    for p in grouped_projects:
        difficulty_stats[p["difficulty"]]["count"] += 1

    payload = {
        "metadata": {
            "title": "Project Based Learning - Interactive Portal",
            "version": "2.0.0",
            "total_raw_entries": len(flat_entries),
            "total_projects": len(grouped_projects),
            "total_languages": len(languages_stats),
            "http_link_count": sum(1 for e in flat_entries if e["is_http"]),
            "languages_stats": list(languages_stats.values()),
            "difficulty_stats": difficulty_stats,
            "lang_meta": LANG_META
        },
        "projects": grouped_projects,
        "raw_entries": flat_entries
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] Generated {OUTPUT_PATH}")
    print(f"Total raw entries: {len(flat_entries)}")
    print(f"Total grouped projects: {len(grouped_projects)}")
    print(f"Total languages: {len(languages_stats)}")
    print("Difficulty breakdown in projects:")
    for k, v in difficulty_stats.items():
        print(f"  Level {k}: {v['count']} projects")

if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    parse_readme_to_projects()
