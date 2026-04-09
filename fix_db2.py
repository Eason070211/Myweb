from app import app, db
app.app_context().push()
db.session.execute(db.text('ALTER TABLE user ADD COLUMN bio TEXT DEFAULT "Explorer | Content Creator | Lifelong Learner\nCreating digital footprints across the web."'))
db.session.commit()
print('Done')