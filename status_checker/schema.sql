drop table if exists books;
create table books (
  id integer primary key autoincrement,
  title text not null,
  author text not null,
  has_read varchar default 'N'
);
