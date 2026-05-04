CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE data_breaches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    reported_date TIMESTAMP WITH TIME ZONE NOT NULL,
    incident_date TIMESTAMP WITH TIME ZONE,
    affected_records_count BIGINT,
    ai_summary TEXT,
    ai_recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_data_breaches_status ON data_breaches(status);
CREATE INDEX idx_data_breaches_severity ON data_breaches(severity);
CREATE INDEX idx_data_breaches_reported_date ON data_breaches(reported_date);
