CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    unformatted_username TEXT NOT NULL,
    password BYTEA NOT NULL,
    salt BYTEA NOT NULL,
    profile TEXT NOT NULL,
    rendered_profile TEXT NOT NULL,
    money BIGINT NOT NULL,
    registration_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    pre_mail_message TEXT,
    last_inbox_view TIMESTAMP WITHOUT TIME ZONE,
    role_id INTEGER NOT NULL -- fkey
);
CREATE INDEX idx__users__unformatted_username ON users (unformatted_username);
    
CREATE TABLE subaccounts (
    subaccount_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL, -- fkey
    name TEXT NOT NULL,
    password BYTEA NOT NULL,
    salt BYTEA NOT NULL,
    CONSTRAINT uniq__subaccounts__user_id__name UNIQUE (user_id, name)
);

CREATE TABLE logins (
    login_id SERIAL PRIMARY KEY,
    code TEXT NOT NULL,
    creation_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    user_id INTEGER NOT NULL, -- fkey
    subaccount_id INTEGER -- fkey
);
CREATE INDEX idx__logins__user_id ON logins (user_id);
CREATE INDEX idx__logins__subaccount_id ON logins (subaccount_id);

CREATE TABLE form_tokens (
    form_token_id SERIAL PRIMARY KEY,
    token TEXT NOT NULL,
    creation_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    user_id INTEGER NOT NULL, -- fkey
    subaccount_id INTEGER -- fkey
);
CREATE INDEX idx__form_tokens__creation_time ON form_tokens (creation_time);
CREATE INDEX idx__form_tokens__user_id__subaccount_id__creation_time__token ON form_tokens (user_id, subaccount_id, creation_time, token);

CREATE TABLE mail_conversations (
    conversation_id SERIAL PRIMARY KEY,
    subject TEXT NOT NULL,
    creation_time TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE mail_participants (
    participant_id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL, -- fkey
    user_id INTEGER NOT NULL, -- fkey
    last_change TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    last_view TIMESTAMP WITHOUT TIME ZONE,
    deleted BOOLEAN NOT NULL,
    system BOOLEAN NOT NULL,
    CONSTRAINT uniq__mail_participants__conversation_id__user_id UNIQUE (conversation_id, user_id)
);
CREATE INDEX idx__mail_participants__conversation_id ON mail_participants (conversation_id);
CREATE INDEX idx__mail_participants__user_id__deleted__last_change ON mail_participants (user_id, deleted, last_change);
CREATE INDEX idx__mail_participants__user_id__deleted__system__last_change ON mail_participants (user_id, deleted, last_change);

CREATE TABLE mail_messages (
    message_id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL, -- fkey
    user_id INTEGER NOT NULL, -- fkey
    message TEXT NOT NULL,
    rendered_message TEXT NOT NULL,
    sent TIMESTAMP WITHOUT TIME ZONE NOT NULL
);
CREATE INDEX idx__mail_messages__conversation_id__sent ON mail_messages (conversation_id, sent);

CREATE TABLE permissions (
    permission_id SERIAL PRIMARY KEY,
    label TEXT CONSTRAINT uniq__permissions__label UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    label TEXT CONSTRAINT uniq__roles__label UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE role_permissions (
    role_id INTEGER, -- fkey
    permission_id INTEGER, -- fkey
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE subaccount_permissions (
    subaccount_id INTEGER, -- fkey
    permission_id INTEGER, -- fkey
    PRIMARY KEY (subaccount_id, permission_id)
);

CREATE TABLE pictures (
    picture_id SERIAL PRIMARY KEY,
    added TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    name TEXT NOT NULL,
    copyright TEXT NOT NULL,
    description TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    format BYTEA NOT NULL,
    image BYTEA NOT NULL
);

CREATE TABLE resized_pictures (
    resized_picture_id SERIAL PRIMARY KEY,
    picture_id INTEGER NOT NULL, -- fkey
    added TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    image BYTEA NOT NULL
);
CREATE INDEX idx__resized_pictures__last_used ON resized_pictures (last_used);
CREATE INDEX idx__resized_pictures__picture_id__width__height ON resized_pictures (picture_id, width, height);

CREATE TABLE species (
    species_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    creatable BOOLEAN NOT NULL
);
CREATE INDEX idx__species__name ON species (name);

CREATE TABLE appearances (
    appearance_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    creatable BOOLEAN NOT NULL
);

CREATE TABLE species_appearances (
    species_id INTEGER, -- fkey
    appearance_id INTEGER, -- fkey
    white_picture_id INTEGER NOT NULL, -- fkey
    black_picture_id INTEGER NOT NULL, -- fkey
    PRIMARY KEY (species_id, appearance_id)
);
CREATE INDEX idx__species_appearances__species_id__appearance_id ON species_appearances (species_id, appearance_id);

CREATE TABLE pets (
    pet_id SERIAL PRIMARY KEY,
    created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    name TEXT NOT NULL,
    unformatted_name TEXT CONSTRAINT uniq__pets__unformatted_name UNIQUE NOT NULL,
    user_id INTEGER NOT NULL, -- fkey
    species_id INTEGER NOT NULL, -- fkey
    appearance_id INTEGER NOT NULL, -- fkey
    color_red INTEGER NOT NULL,
    color_green INTEGER NOT NULL,
    color_blue INTEGER NOT NULL
);
CREATE INDEX idx__pets__unformatted_name ON pets (unformatted_name);
CREATE INDEX idx__pets__user_id ON pets (user_id);

ALTER TABLE users ADD CONSTRAINT fkey__users__role_id FOREIGN KEY (role_id) REFERENCES roles (role_id);
ALTER TABLE subaccounts ADD CONSTRAINT fkey__subaccounts__user_id FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;
ALTER TABLE logins ADD CONSTRAINT fkey__logins__user_id FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;
ALTER TABLE form_tokens ADD CONSTRAINT fkey__form_tokens__user_id FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;
ALTER TABLE form_tokens ADD CONSTRAINT fkey__form_tokens__subaccount_id FOREIGN KEY (subaccount_id) REFERENCES subaccounts (subaccount_id) ON DELETE CASCADE;
ALTER TABLE mail_participants ADD CONSTRAINT fkey__mail_participants__conversation_id FOREIGN KEY (conversation_id) REFERENCES mail_conversations (conversation_id) ON DELETE CASCADE;
ALTER TABLE mail_participants ADD CONSTRAINT fkey__mail_participants__user_id FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;
ALTER TABLE mail_messages ADD CONSTRAINT fkey__mail_messages__conversation_id FOREIGN KEY (conversation_id) REFERENCES mail_conversations (conversation_id) ON DELETE CASCADE;
ALTER TABLE mail_messages ADD CONSTRAINT fkey__mail_messages__user_id FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fkey__role_permissions__role_id FOREIGN KEY (role_id) REFERENCES roles (role_id)  ON DELETE CASCADE;
ALTER TABLE role_permissions ADD CONSTRAINT fkey__role_permissions__permission_id FOREIGN KEY (permission_id) REFERENCES permissions (permission_id) ON DELETE CASCADE;
ALTER TABLE subaccount_permissions ADD CONSTRAINT fkey__subaccount_permissions__subaccount_id FOREIGN KEY (subaccount_id) REFERENCES subaccounts (subaccount_id) ON DELETE CASCADE;
ALTER TABLE subaccount_permissions ADD CONSTRAINT fkey__subaccount_permissions__permission_id FOREIGN KEY (permission_id) REFERENCES permissions (permission_id) ON DELETE CASCADE;
ALTER TABLE resized_pictures ADD CONSTRAINT fkey__resized_pictures__picture_id FOREIGN KEY (picture_id) REFERENCES pictures (picture_id) ON DELETE CASCADE;
ALTER TABLE species_appearances ADD CONSTRAINT fkey__species_appearances__species_id FOREIGN KEY (species_id) REFERENCES species (species_id) ON DELETE CASCADE;
ALTER TABLE species_appearances ADD CONSTRAINT fkey__species_appearances__appearance_id FOREIGN KEY (appearance_id) REFERENCES appearances (appearance_id) ON DELETE CASCADE;
ALTER TABLE species_appearances ADD CONSTRAINT fkey__species_appearances__white_picture_id FOREIGN KEY (white_picture_id) REFERENCES pictures (picture_id);
ALTER TABLE species_appearances ADD CONSTRAINT fkey__species_appearances__black_picture_id FOREIGN KEY (black_picture_id) REFERENCES pictures (picture_id);
ALTER TABLE pets ADD CONSTRAINT fkey__pets__user_id FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE pets ADD CONSTRAINT fkey__pets__species_id__appearance_id FOREIGN KEY (species_id, appearance_id) REFERENCES species_appearances (species_id, appearance_id);