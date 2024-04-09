db = db.getSiblingDB('social_service');
db.createCollection('publications');

db.publications.insertMany([
  {
    "author_user_id": 1,
    "content": "Mi Primera Publicacion :D",
    "created_at": "2024-04-08T23:18:38.196248",
    "updated_at": "2024-04-08T23:18:38.196248"
  },
  {
    "author_user_id": 1,
    "content": "Ya soy influenceeeer",
    "created_at": "2024-04-10T15:11:18.196248",
    "created_at": "2024-04-10T15:11:18.196248"
  }
]);