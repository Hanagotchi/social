db = db.getSiblingDB('social_service');

db.createCollection('posts');
db.createCollection('users');
db.posts.insertMany([
  {
    "author_user_id": 1,
    "content": "Mi Primera Publicacion :D",
    "likes_count" : 0,
    "created_at": ISODate("2024-04-15T05:33:33.127Z"),
    "updated_at":  ISODate("2024-04-15T05:33:33.127Z"),
    "comments": [
      {
        "author": {
          "id": 2,
          "name": "Sofi",
          "photo": "ttps://firebasestorage.googleapis.com/v0/b/hanagotchi.appspot.com/o/users%2Fafirmapaz%40fi.uba.ar%2Favatar%2F1712283245166?alt=media&token=a6923ba4-d4ac-4228-bc12-6791ababfedd",
          "nickname": "chofimpala"
          },
        "content": "bien ahi!!",
        "created_at": ISODate("2024-04-16T05:35:30.127Z")
      }
    ],
    "tags": [],
    "photo_links": [],
  },
  {
    "author_user_id": 1,
    "content": "Ya soy influenceeeer",
    "likes_count" : 0,
    "created_at": ISODate("2024-04-19T02:15:30.217Z"),
    "updated_at": ISODate("2024-04-19T02:15:30.217Z"),
    "tags": ["influencers"],
    "comments": [],
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