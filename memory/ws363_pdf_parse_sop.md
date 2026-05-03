# WS 363 PDF 数据元六字段提取 SOP

## 目标
从 WS 363 系列 PDF 中批量提取 6 字段：数据元标识符、名称、定义、类型、表示格式、允许值。

## 前置
- 安装：pdfplumber
- 路径：F:\Code\GenericAgent\temp\datapricing_skills\test_data\demand_pdf

## 关键坑点
1. 字段值常被换行截断 → 正则用 [\s\S]*? 非贪婪跨行匹配。
2. 块结束标志：下一个“数据元标识符”或文末，正则尾部加 (?=数据元标识符|WS/T|\Z)。
3. 页眉页脚混入 → 先整文档 join 后再切块，避免逐页提取丢失上下文。

## 快速复用脚本
import re, json, pdfplumber, os

def parse_ws363(pdf_path):
    with pdfplumber.open(pdf_path) as doc:
        txt = '\n'.join(p.extract_text() for p in doc.pages if p.extract_text())
    blk_re = re.compile(
        r'数据元标识符\s+([\w.]+)[\s\S]*?'
        r'数据元名称\s+([\s\S]+?)\s*定义\s+([\s\S]+?)\s*'
        r'数据元值的数据类型\s+([\s\S]+?)\s*表示格式\s+([\s\S]+?)\s*'
        r'数据元允许值\s*([\s\S]*?)(?=数据元标识符|WS/T|\Z)', re.M)
    return [dict(zip(['id','name','def','type','format','allow'], m.groups()))
            for m in blk_re.finditer(txt)]

if __name__ == '__main__':
    os.chdir(r'F:\Code\GenericAgent\temp\datapricing_skills\test_data\demand_pdf')
    rows = parse_ws363('卫生健康信息数据元目录 第14部分卫生健康机构（代替WS 363.14—2011）.pdf')
    with open('ws363_14_final.json','w',encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print('提取完成，条数:', len(rows))

## 输出
- 文件：ws363_14_final.json（可替换编号继续后续部分）
- 格式：每对象含 id/name/def/type/format/allow 六键。