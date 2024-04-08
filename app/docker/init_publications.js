db = db.getSiblingDB('social_service');
db.createCollection('publications');

db.publications.insertMany([
  {
    "id_user": 1,
    "content": "Mi Primera Publicacion :D",
    "created_at": "2024-04-08T05:14:02.641Z",
    "updated_at": "2024-04-08T05:14:02.641Z"
  },
  {
    "id_user": 1,
    "content": "Ya soy influenceeeer",
    "created_at": "2024-04-09T05:14:02.641Z",
    "updated_at": "2024-04-09T05:14:02.641Z"
  }
]);