import json
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USER = os.getenv("COGNODB_USER", "cognodb")
PASSWORD = os.getenv("COGNODB_PASSWORD")

if not URI or not PASSWORD:
    raise SystemExit("Set COGNODB_URI and COGNODB_PASSWORD first.")

data = json.loads(
    (Path(__file__).resolve().parent.parent / "data" / "seed.json").read_text()
)

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def seed(tx):
    tx.run("MATCH (n) DETACH DELETE n")

    for person in data["people"]:
        tx.run(
            "MERGE (p:Person {id: $id}) "
            "SET p.name=$name, p.headline=$headline",
            **person,
        )

    for role in data["roles"]:
        tx.run(
            "MERGE (r:Role {id: $id}) "
            "SET r.title=$title, r.level=$level, r.description=$description",
            **role,
        )

    for skill in data["skills"]:
        tx.run(
            "MERGE (s:Skill {id: $id}) "
            "SET s.name=$name, s.category=$category",
            **skill,
        )

    for resource in data["resources"]:
        tx.run(
            "MERGE (l:LearningResource {id: $id}) "
            "SET l.title=$title, l.provider=$provider, l.url=$url",
            **resource,
        )

    for rel in data["person_skills"]:
        tx.run(
            "MATCH (p:Person {id:$person_id}), (s:Skill {id:$skill_id}) "
            "MERGE (p)-[:HAS_SKILL]->(s)",
            **rel,
        )

    for rel in data["role_skills"]:
        tx.run(
            "MATCH (r:Role {id:$role_id}), (s:Skill {id:$skill_id}) "
            "MERGE (r)-[:REQUIRES]->(s)",
            **rel,
        )

    for rel in data["resource_skills"]:
        tx.run(
            "MATCH (l:LearningResource {id:$resource_id}), (s:Skill {id:$skill_id}) "
            "MERGE (l)-[:TEACHES]->(s)",
            **rel,
        )
    for rel in data["targets"]:
        tx.run(
            "MATCH (p:Person {id:$person_id}), (r:Role {id:$role_id}) "
            "MERGE (p)-[:TARGETS]->(r)",
            **rel,
        )

    for rel in data["related_roles"]:
        tx.run(
            "MATCH (a:Role {id:$from_id}), (b:Role {id:$to_id}) "
            "MERGE (a)-[:RELATED_TO]->(b)",
            **rel,
        )


with driver.session() as session:
    session.execute_write(seed)

driver.close()
print("Seed complete.")
