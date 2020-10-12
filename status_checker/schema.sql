drop table if exists books;
create table books (
  id integer primary key autoincrement,
  title text not null,
  author text not null,
  has_read varchar default 'N'
);

drop table if exists books2;
create table books2 (
	id integer primary key autoincrement, 
	title text not null, 
	author text not null, 
	has_read varchar default 'N', 
	created integer not null default (strftime('%s', 'now')), 
	updated integer not null default (strftime('%s', 'now')), 
	notes text default ''
);
