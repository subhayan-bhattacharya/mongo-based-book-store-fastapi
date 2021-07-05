var conn = new Mongo();
var db = conn.getDB("books");
db.books.createIndex({"name": 1}, {"unique": true});
db.authors.createIndex({"name": 1}, {"unique": true});
db.genres.createIndex({"name": 1}, {"unique": true});
