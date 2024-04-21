create sequence platform_platformid_seq
    as integer;

create table "Player"
(
    username      varchar(255)       not null
        constraint username
            primary key,
    first_name    varchar(255)       not null,
    last_name     varchar(255)       not null,
    creation_date date default now() not null,
    last_online   date default now() not null,
    password      bytea              not null,
    salt          bytea              not null
);

create table "Friends"
(
    username varchar(255) not null
        constraint friends___fk
            references "Player",
    friend   varchar(255) not null
        constraint friends_user_username_fk
            references "Player",
    unique (username, friend)
);

create table "Platform"
(
    platformid integer default nextval('platform_platformid_seq'::regclass) not null
        constraint platform_pk
            primary key,
    name       varchar(255)
        unique
);

alter sequence platform_platformid_seq owned by "Platform".platformid;

create table "Emails"
(
    username varchar(255) not null
        constraint emails_user_username_fk
            references "Player",
    email    varchar(255) not null,
    constraint emails_pk
        primary key (username, email)
);

create table "OwnsPlatform"
(
    platformid integer,
    username   varchar(255)
        constraint ownsplatform_username_fkey
            references "Player",
    constraint ownsplatform_platformid_username_key
        unique (platformid, username)
);

create table "Game"
(
    gameid      integer generated always as identity
        constraint game_pk
            primary key,
    title       varchar(255) not null,
    esrb_rating varchar(32)
        constraint esrb_rating_domain
            check ((esrb_rating)::bpchar = ANY
                   (ARRAY ['Everyone'::bpchar, 'Everyone 10+'::bpchar, 'Teen'::bpchar, 'Mature 17+'::bpchar, 'Adults Only 18+'::bpchar, 'Rating Pending'::bpchar, 'Rating Pending Likely Mature 17+'::bpchar])),
    publisher   varchar(255),
    unique (title, publisher)
);

create table "GameOnPlatform"
(
    gameid       integer not null
        references "Game",
    platformid   integer not null
        references "Platform",
    price        real,
    release_date date,
    unique (gameid, platformid)
);

create table "Collection"
(
    collectionid integer generated always as identity
        constraint collection_pk
            primary key,
    username     varchar(255)          not null
        constraint collection_user_username_fk
            references "Player",
    title        varchar(255)          not null,
    visible      boolean default false not null,
    unique (username, title)
);

create table "Development"
(
    gameid    integer      not null
        constraint development_gameid_fkey
            references "Game",
    developer varchar(255) not null,
    constraint development_gameid_developer_key
        unique (gameid, developer)
);

create table "OwnsGame"
(
    gameid      integer      not null
        constraint curr_game
            references "Game",
    username    varchar(255) not null
        constraint curr_user
            references "Player",
    star_rating integer,
    review_text text,
    constraint primary_key
        primary key (gameid, username)
);

create table "Genre"
(
    gameid     integer      not null
        constraint genre_gameid_fkey
            references "Game",
    genre_name varchar(255) not null,
    constraint genre_gameid_genre_name_key
        unique (gameid, genre_name)
);

create table "CollectionContains"
(
    collectionid integer not null
        constraint collectioncontains_collection_collectionid_fk
            references "Collection",
    gameid       integer not null
        constraint collectioncontains_game_gameid_fk
            references "Game",
    constraint collectioncontains_pk
        primary key (collectionid, gameid)
);

create table "PlaysGame"
(
    gameid     integer      not null
        constraint playsgame_game_gameid_fk
            references "Game",
    username   varchar(255) not null
        constraint playsgame_player_username_fk
            references "Player",
    start_time timestamp    not null,
    end_time   timestamp    not null,
    constraint playsgame___pk
        primary key (gameid, username, start_time, end_time)
);


