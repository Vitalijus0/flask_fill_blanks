create table users (
    id serial primary key,
    name text not null,
    password text not null,
    expert boolean not null,
    admin boolean not null 
);

create table questions (
    id serial primary key,
    question_text text not null,
    answer_text text,
    asked_by_id integer not null,
    expert_id integer not null
);

create table comments (
    id serial primary key,
    comment_text text not null,
    commented_by_id integer not null
);