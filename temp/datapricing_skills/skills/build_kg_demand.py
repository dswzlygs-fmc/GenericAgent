#!/usr/bin/env python3
"""
Skill: build_kg_demand
功能：将卫生健康信息数据元目录PDF批量解析为Neo4j图谱（DemandDataElement+MetaDataElement+HAS_META）
用法：build_kg_demand(pdf_dir, clear=True)
"""
import os, re, uuid, csv
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
import neo4j, pdfplumber

load_dotenv(Path(__file__).parent.parent / '.env')
URI = os.getenv('NEO4J_URI')
USER = os.getenv('NEO4J_USER')
PWD = os.getenv('NEO4J_PASSWORD')

def _extract_elements(text: str) -> List[Dict]:
    chunks = re.split(r'数据元标识符\s+', text)[1:]
    elements = []
    for chunk in chunks:
        m = re.search(
            r'^(DE[0-9.]+)\s+'
            r'数据元名称\s+([^\n]+)\s+'
            r'定义\s+([^\n]+(?:\n[^数据元].*?)*)\s+'
            r'数据元值的数据类型\s+([A-Z0-9]+)\s+'
            r'表示格式\s+([^\n]+)\s+'
            r'数据元允许值\s+([^\n]+)',
            chunk, re.MULTILINE | re.DOTALL
        )
        if m:
            elements.append({
                'identifier': m.group(1).strip(),
                'name': m.group(2).strip(),
                'definition': m.group(3).replace('\n',' ').strip(),
                'dataType': m.group(4).strip(),
                'format': m.group(5).strip(),
                'allowValue': m.group(6).strip()
            })
    return elements

def build_kg_demand(pdf_dir: str, clear: bool = True) -> str:
    pdf_dir = Path(pdf_dir)
    driver = neo4j.GraphDatabase.driver(URI, auth=(USER, PWD))
    kg_id = f'demand_full_kg_{uuid.uuid4().hex[:8]}'
    with driver.session() as s:
        if clear:
            s.run('MATCH (n) DETACH DELETE n')
        meta_csv = Path(__file__).parent.parent / 'test_data' / 'ws363_meta.csv'
        if meta_csv.exists():
            with meta_csv.open(encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    s.run('MERGE (m:MetaDataElement {metaType: $metaType}) ON CREATE SET m.id=randomUUID(), m.description=$description', row)
        for pdf_path in pdf_dir.glob('WS 363.*—*.pdf'):
            part_match = re.search(r'第(\d+)部分', pdf_path.stem)
            if not part_match:
                continue
            part = part_match.group(1)
            with pdfplumber.open(pdf_path) as pdf:
                text = ''.join([p.extract_text() or '' for p in pdf.pages])
            elements = _extract_elements(text)
            for el in elements:
                el['id'] = str(uuid.uuid4())
                el['sourcePart'] = part
                el['kgId'] = kg_id
                s.run('CREATE (d:DemandDataElement {id:$id, identifier:$identifier, name:$name, definition:$definition, dataType:$dataType, format:$format, allowValue:$allowValue, sourcePart:$sourcePart, kgId:$kgId})', el)
                s.run('MATCH (d:DemandDataElement {id:$id}) MERGE (mf:MetaDataElement {metaType: d.format}) ON CREATE SET mf.id=randomUUID(), mf.description="格式说明见总则附录" WITH d, mf CREATE (d)-[:HAS_META]->(mf)', {'id': el['id']})
        total = s.run('MATCH (n:DemandDataElement) RETURN count(*) as c').single()['c']
        print('✔ 批量入库完成，节点数：', total, '| 图谱ID：', kg_id)
    driver.close()
    return kg_id

if __name__ == '__main__':
    build_kg_demand('./datapricing_skills/test_data/demand_pdf')
