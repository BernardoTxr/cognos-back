-- Enums
CREATE TYPE sexo AS ENUM ('masc', 'fem');

CREATE TYPE nivel_tea AS ENUM ('nivel_1', 'nivel_2', 'nivel_3');

-- Table: users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    superAdmin BOOLEAN,
    password VARCHAR NOT NULL
);

-- Table: paciente
CREATE TABLE paciente (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR NOT NULL,
    nome_completo VARCHAR NOT NULL,
    data_de_nascimento TIMESTAMP,
    email VARCHAR NOT NULL,
    cpf VARCHAR(14),
    sexo sexo,
    nivel_tea nivel_tea,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: terapeuta
CREATE TABLE terapeuta (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR NOT NULL,
    nome_completo VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    documento VARCHAR NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Table: paciente_terapeuta
CREATE TABLE paciente_terapeuta (
    id SERIAL PRIMARY KEY,
    paciente_id UUID REFERENCES paciente(user_id) ON DELETE CASCADE,
    terapeuta_id UUID REFERENCES terapeuta(user_id) ON DELETE CASCADE
);

-- Table: jogo
CREATE TABLE jogo (
    id SERIAL PRIMARY KEY,
    nome VARCHAR NOT NULL
);

-- Table: partida
CREATE TABLE partida (
    id SERIAL PRIMARY KEY,
    jogo_id INTEGER REFERENCES jogo(id) ON DELETE CASCADE,
    paciente_id UUID REFERENCES paciente(user_id) ON DELETE CASCADE,
    results VARCHAR,
    duration INTEGER,
    played_at TIMESTAMP DEFAULT NOW()
);

-- Table: topico_wiki
CREATE TABLE topico_wiki (
    id SERIAL PRIMARY KEY,
    topico VARCHAR NOT NULL
);

-- Table: conceitos_wiki
CREATE TABLE conceitos_wiki (
    id SERIAL PRIMARY KEY,
    autor UUID REFERENCES terapeuta(user_id) ON DELETE SET NULL,
    topico INTEGER REFERENCES topico_wiki(id) ON DELETE CASCADE,
    conceito VARCHAR NOT NULL,
    definicao VARCHAR NOT NULL,
    approved BOOLEAN DEFAULT NULL,
    motivo_rejeicao VARCHAR DEFAULT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT motivo_rejeicao_check CHECK (
        (approved IS TRUE AND motivo_rejeicao IS NULL)
        OR
        (approved IS FALSE AND motivo_rejeicao IS NOT NULL)
        OR
        approved IS NULL
    )
);
