lot_published_update_query = '''UPDATE lot l
SET l.status = 'lot.published'
WHERE l.active = 1
AND l.archive = 0
AND l.actualId IS NULL
AND l.procedureId = '%s'
;'''

procedure_published_update_query = '''UPDATE procedures p
SET p.status = 'procedure.published'
WHERE p.id = '%s'
;'''