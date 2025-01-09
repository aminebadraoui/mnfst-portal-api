CREATE TABLE IF NOT EXISTS story_based_advertorials (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content JSONB,
    status VARCHAR NOT NULL,
    error VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_story_based_advertorials_project_id ON story_based_advertorials(project_id);
CREATE INDEX IF NOT EXISTS ix_story_based_advertorials_user_id ON story_based_advertorials(user_id);

CREATE TABLE IF NOT EXISTS value_based_advertorials (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content JSONB,
    status VARCHAR NOT NULL,
    error VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_value_based_advertorials_project_id ON value_based_advertorials(project_id);
CREATE INDEX IF NOT EXISTS ix_value_based_advertorials_user_id ON value_based_advertorials(user_id);

CREATE TABLE IF NOT EXISTS informational_advertorials (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content JSONB,
    status VARCHAR NOT NULL,
    error VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_informational_advertorials_project_id ON informational_advertorials(project_id);
CREATE INDEX IF NOT EXISTS ix_informational_advertorials_user_id ON informational_advertorials(user_id); 