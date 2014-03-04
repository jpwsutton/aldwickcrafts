drop table if exists products;
create table products (
        id integer primary key autoincrement,
        name text not null,
        description text not null,
        category text not null,
        image text not null,
        price text not null
);

