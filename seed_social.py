from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.post import Post
from app.models.postMedia import PostMedia
from app.models.story import Story
from app.models.Enums import PostType, StoryType
from datetime import datetime, timedelta
import os

app = create_app("development")
# Ensure we use the same DB as init_db.py
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/sf_collab_dev.db'

with app.app_context():
    print("Seeding social content...")
    user = User.query.filter_by(email="test@example.com").first()
    if not user:
        print("Error: Test user not found. Run init_db.py first.")
        exit(1)

    # 1. Text-only post
    post1 = Post(
        user_id=user.id,
        author_id=user.id,
        author_first_name=user.first_name,
        author_last_name=user.last_name,
        content="This is a text-only post for E2E testing. #sfcollab #test",
        type=PostType.text
    )
    db.session.add(post1)

    # 2. Post with picture
    post2 = Post(
        user_id=user.id,
        author_id=user.id,
        author_first_name=user.first_name,
        author_last_name=user.last_name,
        content="This is a post with an image! #visuals",
        type=PostType.image
    )
    db.session.add(post2)
    db.session.flush() # get post2.id

    media1 = PostMedia(
        post_id=post2.id,
        content_type="image/jpeg",
        file_name="test_image.jpg",
        file_size=1024,
        caption="Sample Image",
        data=b"dummy image data"
    )
    db.session.add(media1)

    # 3. Post with video
    post3 = Post(
        user_id=user.id,
        author_id=user.id,
        author_first_name=user.first_name,
        author_last_name=user.last_name,
        content="This is a post with a video! #motion",
        type=PostType.video
    )
    db.session.add(post3)
    db.session.flush() # get post3.id

    media2 = PostMedia(
        post_id=post3.id,
        content_type="video/mp4",
        file_name="test_video.mp4",
        file_size=2048,
        caption="Sample Video",
        data=b"dummy video data"
    )
    db.session.add(media2)

    # 4. Story
    story1 = Story(
        user_id=user.id,
        author_id=user.id,
        author_first_name=user.first_name,
        author_last_name=user.last_name,
        media_url="https://via.placeholder.com/1080x1920?text=Sample+Story",
        caption="A sample story for E2E testing!",
        type=StoryType.image,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db.session.add(story1)

    db.session.commit()
    print("Social content seeded successfully.")
