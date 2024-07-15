from app import db

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_count = db.Column(db.Integer, default=0)
    image_count = db.Column(db.Integer, default=0)

    def increment_message_count(self):
        self.message_count += 1
        db.session.commit()

    def increment_image_count(self):
        self.image_count += 1
        db.session.commit()

    def reset_stats(self):
        self.message_count = 0
        self.image_count = 0
        db.session.commit()
