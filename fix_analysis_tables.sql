-- Drop existing tables
DROP TABLE IF EXISTS avatar_analysis CASCADE;
DROP TABLE IF EXISTS pain_analysis CASCADE;
DROP TABLE IF EXISTS pattern_analysis CASCADE;
DROP TABLE IF EXISTS product_analysis CASCADE;
DROP TABLE IF EXISTS question_analysis CASCADE;

-- Create avatar_analysis table
CREATE TABLE avatar_analysis (
    id UUID PRIMARY KEY,
    task_id UUID UNIQUE NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'processing',
    analysis_type VARCHAR NOT NULL DEFAULT 'Avatars',
    query VARCHAR,
    insights JSONB DEFAULT '{}',
    raw_perplexity_response VARCHAR,
    error VARCHAR,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create pain_analysis table
CREATE TABLE pain_analysis (
    id UUID PRIMARY KEY,
    task_id UUID UNIQUE NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'processing',
    analysis_type VARCHAR NOT NULL DEFAULT 'Pain & Frustration Analysis',
    query VARCHAR,
    insights JSONB DEFAULT '{}',
    raw_perplexity_response VARCHAR,
    error VARCHAR,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create pattern_analysis table
CREATE TABLE pattern_analysis (
    id UUID PRIMARY KEY,
    task_id UUID UNIQUE NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'processing',
    analysis_type VARCHAR NOT NULL DEFAULT 'Pattern Detection',
    query VARCHAR,
    insights JSONB DEFAULT '{}',
    raw_perplexity_response VARCHAR,
    error VARCHAR,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create product_analysis table
CREATE TABLE product_analysis (
    id UUID PRIMARY KEY,
    task_id UUID UNIQUE NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'processing',
    analysis_type VARCHAR NOT NULL DEFAULT 'Popular Products Analysis',
    query VARCHAR,
    insights JSONB DEFAULT '{}',
    raw_perplexity_response VARCHAR,
    error VARCHAR,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create question_analysis table
CREATE TABLE question_analysis (
    id UUID PRIMARY KEY,
    task_id UUID UNIQUE NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'processing',
    analysis_type VARCHAR NOT NULL DEFAULT 'Question & Advice Mapping',
    query VARCHAR,
    insights JSONB DEFAULT '{}',
    raw_perplexity_response VARCHAR,
    error VARCHAR,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Create indexes
CREATE INDEX ix_avatar_analysis_user_project ON avatar_analysis(user_id, project_id);
CREATE INDEX ix_avatar_analysis_project_query ON avatar_analysis(project_id, query);
CREATE INDEX ix_avatar_analysis_task_id ON avatar_analysis(task_id);

CREATE INDEX ix_pain_analysis_user_project ON pain_analysis(user_id, project_id);
CREATE INDEX ix_pain_analysis_project_query ON pain_analysis(project_id, query);
CREATE INDEX ix_pain_analysis_task_id ON pain_analysis(task_id);

CREATE INDEX ix_pattern_analysis_user_project ON pattern_analysis(user_id, project_id);
CREATE INDEX ix_pattern_analysis_project_query ON pattern_analysis(project_id, query);
CREATE INDEX ix_pattern_analysis_task_id ON pattern_analysis(task_id);

CREATE INDEX ix_product_analysis_user_project ON product_analysis(user_id, project_id);
CREATE INDEX ix_product_analysis_project_query ON product_analysis(project_id, query);
CREATE INDEX ix_product_analysis_task_id ON product_analysis(task_id);

CREATE INDEX ix_question_analysis_user_project ON question_analysis(user_id, project_id);
CREATE INDEX ix_question_analysis_project_query ON question_analysis(project_id, query);
CREATE INDEX ix_question_analysis_task_id ON question_analysis(task_id); 