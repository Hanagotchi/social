db = db.getSiblingDB('social_service');

db.createCollection('posts');
db.createCollection('users');

db.posts.insertMany([
  {
    "author_user_id": 1,
    "content": "Mi Primera Publicacion :D",
    "likes_count" : 0,
    "created_at": "2024-04-08T23:18:38.196248",
    "updated_at": "2024-04-08T23:18:38.196248",
    "photo_links": []
  },
  {
    "author_user_id": 1,
    "content": "Ya soy influenceeeer",
    "likes_count" : 0,
    "created_at": "2024-04-10T15:11:18.196248",
    "updated_at": "2024-04-10T15:11:18.196248",
    "photo_links": []
  }
])

// https://github.com/Hanagotchi/users/blob/master/app/docker/tablas.sql 
// create the users collection with the same structure as the users table!
db.users.insertMany([
  {
    "_id": 1,
    "followers": [],
    "following": [],
    "tags": []
  }],
  {
    "_id": 2,
    "followers": [],
    "following": [],
    "tags": []
  },
  {
    "_id": 3,
    "followers": [],
    "following": [],
    "tags": []
  },
  {
    "_id": 4,
    "followers": [],
    "following": [],
    "tags": []
  }
)