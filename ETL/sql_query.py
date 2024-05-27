person_query: str = """
    select p.id, p.full_name,
    array_agg(DISTINCT pfw.role) as role,
    array_agg(DISTINCT pfw.film_work_id)::text[] as film_ids,
    p.modified 
    FROM content.person as p
    left join content.person_film_work as pfw on pfw.person_id = p.id
    WHERE p.modified > %(state)s
    group by p.id
    order by modified;
"""

film_query = '''SELECT
   fw.id,
   fw.title,
   fw.description,
   fw.rating,
   fw.type,
   fw.created,
   fw.modified,
   COALESCE (
       json_agg(
           DISTINCT jsonb_build_object(
               'person_role', pfw.role,
               'person_id', p.id,
               'person_name', p.full_name
           )
       ) FILTER (WHERE p.id is not null),
       '[]'
   ) as persons,
   array_agg(DISTINCT g.name) as genres
FROM content.film_work fw
LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
LEFT JOIN content.person p ON p.id = pfw.person_id
LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
LEFT JOIN content.genre g ON g.id = gfw.genre_id
WHERE fw.modified > %(state)s OR p.modified > %(state)s OR g.modified > %(state)s
GROUP BY fw.id
ORDER BY fw.modified;'''


genre_query = '''
select g.id, g.name, g.modified
FROM content.genre g
WHERE g.modified > %(state)s;
'''