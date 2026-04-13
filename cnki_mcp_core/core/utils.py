import os

def calculate_similarity(s1: str, s2: str) -> float:
    """简单的字符重合度评分"""
    if not s1 or not s2: return 0.0
    s1, s2 = s1.lower(), s2.lower()
    common = sum(1 for char in s1 if char in s2)
    return common / max(len(s1), len(s2))


def _generate_ris(paper: dict) -> str:
    """将知网论文数据转换为标准 RIS 格式"""
    lines = ["TY  - JOUR"]
    
    # 标题
    if paper.get("title"):
        lines.append(f"TI  - {paper['title']}")
    
    # 作者
    authors = paper.get("authors", [])
    if isinstance(authors, str): authors = [authors]
    for author in authors:
        lines.append(f"AU  - {author}")
    
    # 刊名/来源
    if paper.get("source"):
        lines.append(f"JO  - {paper['source']}")
    
    # DOI
    if paper.get("doi"):
        lines.append(f"DO  - {paper['doi']}")
    
    # 摘要
    if paper.get("abstract"):
        lines.append(f"AB  - {paper['abstract']}")
    
    # 关键词
    keywords = paper.get("keywords", [])
    if isinstance(keywords, str): keywords = [keywords]
    for kw in keywords:
        lines.append(f"KW  - {kw}")
    
    # 日期 (提取年份)
    date = paper.get("date", "")
    if date and len(date) >= 4:
        lines.append(f"PY  - {date[:4]}")
    
    # URL
    if paper.get("url"):
        lines.append(f"UR  - {paper['url']}")
    
    lines.append("ER  - ")
    return "\n".join(lines)


def get_safe_filename(title: str) -> str:
    """提取并在文件名中过滤非法字符"""
    if not title:
        return "unknown_paper"
    return "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip()
