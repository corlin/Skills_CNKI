# Core constants for CNKI MCP

SEARCH_MODES = {
    "主题": "SU", "篇名": "TI", "关键词": "KY", "全文": "FT",
    "作者": "AU", "第一作者": "FI", "通讯作者": "RP", "作者单位": "AF",
    "基金": "FU", "摘要": "AB", "DOI": "DOI", "全文": "FT"
}

# 英文别名映射
SEARCH_MODE_ALIASES = {
    "subject": "主题", "title": "篇名", "keyword": "关键词", "author": "作者",
    "institution": "作者单位", "abstract": "摘要", "doi": "DOI"
}

SORT_MODES = {
    "相关度": "FFD", "发表时间": "PT", "被引": "CF", "下载": "DFR"
}
