import json
import re

def clean_content(text: str) -> str:
    # 移除 markdown 图片引用
    text = re.sub(r'!\[\]\(.*?\)', '', text)
    # 移除图片路径（包括残缺链接）
    text = re.sub(r'[^\s]*\.(jpg|jpeg|png|gif|bmp)\)?', '', text, flags=re.IGNORECASE)
    # 移除 HTML 表格块
    text = re.sub(r'<table.*?</table>', '', text, flags=re.S)
    # 移除所有 HTML 标签
    text = re.sub(r'<.*?>', '', text)
    # 移除 markdown 标题
    text = re.sub(r'#.*', '', text)

    # 移除 minerU 残留的 gMASK / MASK 等无效 token
    text = re.sub(r'\b(g?MASK\]?[\w/>]*)', '', text, flags=re.IGNORECASE)
    # 清除 HTML 残留标签头（td, tr, etc.）
    text = re.sub(r'\b(td|tr|th|col|br|row|tbody|thead)[ >:/]?', '', text, flags=re.IGNORECASE)

    # 移除特定垃圾字段
    garbage_phrases = [
        r'phone number[:：]?', r'email[:：]?', r'service address[:：]?',
        r'system (type|serial number|part number|software version|revision)[:：]?',
        r'hours of work[:：]?', r'contact renishaw.*', r'refer to.*'
    ]
    for pattern in garbage_phrases:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    # 删除成对未匹配的残留符号
    text = re.sub(r'\[\s*', '', text)        # 去掉孤立 [
    text = re.sub(r'\(\s*', '', text)        # 去掉孤立 (
    text = re.sub(r'\s*\]', '', text)        # 去掉孤立 ]
    text = re.sub(r'\s*\)', '', text)        # 去掉孤立 )
    text = re.sub(r'\(\s*\)', '', text)      # 空括号 ()
    text = re.sub(r'\[\s*\]', '', text)      # 空中括号 []

    # 清理多余空白字符
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)

    return text.strip()

# 加载 chunk 数据
with open("chunk_data_with_description.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# 就地修改 content 字段
for chunk in chunks:
    chunk["content"] = clean_content(chunk["content"])

# 保存结果
with open("chunk_data_content_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print("已清洗完成，覆盖 content 字段，保存为 chunk_data_content_cleaned.json")
