-- Add Telegram integration tables

-- Telegram Users table for linking accounts
CREATE TABLE telegram_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    telegram_id BIGINT UNIQUE NOT NULL,
    telegram_username VARCHAR(255),
    telegram_first_name VARCHAR(255),
    telegram_last_name VARCHAR(255),
    is_linked BOOLEAN DEFAULT false,
    link_token VARCHAR(255) UNIQUE,
    link_token_expires_at TIMESTAMP WITH TIME ZONE,
    linked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for performance
CREATE INDEX idx_telegram_users_telegram_id ON telegram_users(telegram_id);
CREATE INDEX idx_telegram_users_user_id ON telegram_users(user_id);
CREATE INDEX idx_telegram_users_link_token ON telegram_users(link_token);

-- Trigger for updated_at
CREATE TRIGGER update_telegram_users_updated_at BEFORE UPDATE ON telegram_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add telegram_id to users table for quick lookup (optional)
ALTER TABLE users ADD COLUMN telegram_user_id UUID REFERENCES telegram_users(id);