db = db.getSiblingDB('social_service');

db.createCollection('posts');
db.createCollection('users');
db.posts.insertMany([
  {
    "author_user_id": 17,
    "content": "Mi Primera Publicacion :D",
    "likes_count" : 0,
    "created_at": ISODate("2024-04-15T05:33:33.127Z"),
    "updated_at":  ISODate("2024-04-15T05:33:33.127Z"),
    "comments": [
      {
        "id": "fdfe6218-64f7-4f89-af36-42b8b035f4c8",
        "author": 11,
        "content": "bien ahi!!",
        "created_at": ISODate("2024-04-16T05:35:30.127Z")
      }
    ],
    "comments_count": 1,
    "tags": [],
    "photo_links": [],
  },
  {
    "author_user_id": 17,
    "content": "Ya soy influenceeeer",
    "likes_count" : 0,
    "created_at": ISODate("2024-04-19T02:15:30.217Z"),
    "updated_at": ISODate("2024-04-19T02:15:30.217Z"),
    "tags": ["influencers"],
    "comments": [],
    "comments_count": 0,
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
  },
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
])