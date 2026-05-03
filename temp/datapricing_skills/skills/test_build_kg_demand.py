import pytest, uuid, os
from pathlib import Path
from dotenv import load_dotenv
import neo4j
from build_kg_demand import build_kg_demand

load_dotenv(Path(__file__).parent.parent / '.env')
URI = os.getenv('NEO4J_URI')
USER = os.getenv('NEO4J_USER')
PWD = os.getenv('NEO4J_PASSWORD')

def test_build_kg_demand():
    driver = neo4j.GraphDatabase.driver(URI, auth=(USER, PWD))
    kg_id = build_kg_demand('./datapricing_skills/test_data/demand_pdf', clear=True)
    with driver.session() as s:
        total = s.run('MATCH (n:DemandDataElement) RETURN count(*) as c').single()['c']
        assert total > 1000, f'预期>1000节点，实际{total}'
        meta = s.run('MATCH (m:MetaDataElement) RETURN count(*) as c').single()['c']
        assert meta >= 11, f'预期≥11总则节点，实际{meta}'
        rel = s.run('MATCH ()-[:HAS_META]->() RETURN count(*) as c').single()['c']
        assert rel == total, f'关系数应等于节点数，实际{rel}'
    driver.close()
    print('✔ pytest通过，图谱ID：', kg_id)

if __name__ == '__main__':
    test_build_kg_demand()
