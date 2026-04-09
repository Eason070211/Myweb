from app import app, db
app.app_context().push()
db.session.execute(db.text('ALTER TABLE user ADD COLUMN status VARCHAR(100) DEFAULT "Exploring"'))
db.session.commit()
print('Done')