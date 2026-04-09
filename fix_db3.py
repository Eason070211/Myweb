from app import app, db
app.app_context().push()
db.session.execute(db.text('ALTER TABLE user ADD COLUMN theme_enabled BOOLEAN DEFAULT 0'))
db.session.commit()
print('Done')