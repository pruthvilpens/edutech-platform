-- Migration: Create WhatsApp Users Table
-- Description: Add WhatsApp integration support with user linking functionality
-- Date: 2025-01-01

BEGIN;

-- Create whatsapp_users table
CREATE TABLE IF NOT EXISTS whatsapp_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    whatsapp_phone VARCHAR(20) UNIQUE NOT NULL,
    whatsapp_name VARCHAR(255),
    whatsapp_profile_name VARCHAR(255),
    is_linked BOOLEAN DEFAULT FALSE,
    link_token VARCHAR(255) UNIQUE,
    link_token_expires_at TIMESTAMP WITH TIME ZONE,
    linked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_whatsapp_users_phone ON whatsapp_users(whatsapp_phone);
CREATE INDEX IF NOT EXISTS idx_whatsapp_users_user_id ON whatsapp_users(user_id);
CREATE INDEX IF NOT EXISTS idx_whatsapp_users_link_token ON whatsapp_users(link_token);
CREATE INDEX IF NOT EXISTS idx_whatsapp_users_is_linked ON whatsapp_users(is_linked);

-- Add updated_at trigger
CREATE OR REPLACE FUNCTION update_whatsapp_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_whatsapp_users_updated_at
    BEFORE UPDATE ON whatsapp_users
    FOR EACH ROW
    EXECUTE FUNCTION update_whatsapp_users_updated_at();

-- Add comments for documentation
COMMENT ON TABLE whatsapp_users IS 'WhatsApp user accounts and their linking status to platform users';
COMMENT ON COLUMN whatsapp_users.id IS 'Primary key UUID';
COMMENT ON COLUMN whatsapp_users.user_id IS 'Foreign key to users table, nullable until linked';
COMMENT ON COLUMN whatsapp_users.whatsapp_phone IS 'WhatsApp phone number (unique identifier)';
COMMENT ON COLUMN whatsapp_users.whatsapp_name IS 'WhatsApp display name';
COMMENT ON COLUMN whatsapp_users.whatsapp_profile_name IS 'WhatsApp profile name';
COMMENT ON COLUMN whatsapp_users.is_linked IS 'Whether this WhatsApp account is linked to a platform user';
COMMENT ON COLUMN whatsapp_users.link_token IS 'Temporary token for account linking process';
COMMENT ON COLUMN whatsapp_users.link_token_expires_at IS 'Expiration time for link token';
COMMENT ON COLUMN whatsapp_users.linked_at IS 'Timestamp when account was linked';
COMMENT ON COLUMN whatsapp_users.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN whatsapp_users.updated_at IS 'Last update timestamp';

COMMIT;