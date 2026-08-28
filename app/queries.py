# All application Cypher lives here.
# Every user-controlled value is passed as a parameter.

ROLES = """
MATCH (r:Role)
OPTIONAL MATCH (r)-[:REQUIRES]->(s:Skill)
RETURN r.id AS id, r.title AS title, r.level AS level,
       r.description AS description,
       collect(s.name) AS skills
ORDER BY r.title
"""

ROLE_DETAIL = """
MATCH (r:Role {id: $role_id})
OPTIONAL MATCH (r)-[:REQUIRES]->(s:Skill)
OPTIONAL MATCH (r)-[:RELATED_TO]->(related:Role)
RETURN r.id AS id, r.title AS title, r.level AS level,
       r.description AS description,
       collect(DISTINCT s.name) AS skills,
       collect(DISTINCT {id: related.id, title: related.title}) AS related
"""

PROFILE = """
MATCH (p:Person {id: $person_id})
OPTIONAL MATCH (p)-[:HAS_SKILL]->(s:Skill)
OPTIONAL MATCH (p)-[:TARGETS]->(r:Role)
RETURN p.id AS id, p.name AS name, p.headline AS headline,
       collect(DISTINCT s.name) AS skills,
       collect(DISTINCT {id: r.id, title: r.title}) AS targets
"""

SKILL_GAP = """
MATCH (p:Person {id: $person_id}), (r:Role {id: $role_id})
OPTIONAL MATCH (r)-[:REQUIRES]->(required:Skill)
WITH p, r, required
OPTIONAL MATCH (p)-[:HAS_SKILL]->(owned:Skill)
WITH r, required, collect(owned.name) AS owned_names
WHERE required IS NOT NULL AND NOT required.name IN owned_names
OPTIONAL MATCH (resource:LearningResource)-[:TEACHES]->(required)
RETURN required.name AS skill,
       required.category AS category,
       collect(DISTINCT {
           id: resource.id,
           title: resource.title,
           provider: resource.provider,
           url: resource.url
       })[0..3] AS resources
ORDER BY category, skill
"""

RECOMMEND_ROLES = """
MATCH (p:Person {id: $person_id})-[:HAS_SKILL]->(s:Skill)<-[:REQUIRES]-(r:Role)
WITH p, r, count(DISTINCT s) AS overlap
OPTIONAL MATCH (r)-[:REQUIRES]->(allSkills:Skill)
WITH p, r, overlap, count(DISTINCT allSkills) AS total_required
RETURN r.id AS id, r.title AS title, r.level AS level,
       overlap, total_required,
       round(100.0 * overlap /
         CASE WHEN total_required = 0 THEN 1 ELSE total_required END
       ) AS match_percent
ORDER BY match_percent DESC, overlap DESC, r.title
LIMIT 8
"""

LEARNING_PATH = """
MATCH (p:Person {id: $person_id}), (r:Role {id: $role_id})
MATCH (r)-[:REQUIRES]->(target:Skill)
WHERE NOT (p)-[:HAS_SKILL]->(target)
OPTIONAL MATCH (resource:LearningResource)-[:TEACHES]->(target)
RETURN target.name AS skill,
       target.category AS category,
       collect(DISTINCT {
           title: resource.title,
           provider: resource.provider,
           url: resource.url
       })[0..3] AS resources
ORDER BY category, skill
"""

GRAPH = """
MATCH (p:Person {id: $person_id})-[:HAS_SKILL]->(s:Skill)
OPTIONAL MATCH (s)<-[:REQUIRES]-(r:Role)
OPTIONAL MATCH (r)-[:REQUIRES]->(adjacent:Skill)
RETURN p.name AS person,
       collect(DISTINCT {id: s.id, label: s.name, type: 'skill'}) AS owned_skills,
       collect(DISTINCT {id: r.id, label: r.title, type: 'role'}) AS roles,
       collect(DISTINCT {id: adjacent.id, label: adjacent.name, type: 'skill'}) AS adjacent_skills
"""
