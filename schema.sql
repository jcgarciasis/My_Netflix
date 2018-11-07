drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null unique,
  pass text not null,
  creditcard integer,
  cvv integer,
  payment text not null
);