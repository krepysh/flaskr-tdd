from project.app import db
from project.models import Post

db.create_all()
db.session.add(Post(title="ttitle", body="tbody"))
db.session.commit()
