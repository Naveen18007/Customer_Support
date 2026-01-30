-- ============================================
-- UPDATED SUPABASE SCHEMA FOR CUSTOMER SUPPORT
-- ============================================

-- Drop existing tables if needed (use with caution in production)
-- DROP TABLE IF EXISTS technical_issues CASCADE;
-- DROP TABLE IF EXISTS billing CASCADE;
-- DROP TABLE IF EXISTS faqs CASCADE;
-- DROP TABLE IF EXISTS accounts CASCADE;

-- ============================================
-- ACCOUNTS TABLE (Updated with DOB field)
-- ============================================
CREATE TABLE IF NOT EXISTS accounts (
    customer_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    phone VARCHAR(20),
    dob DATE,  -- Added: Date of Birth field for account updates
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- ============================================
-- BILLING TABLE (Updated to support both orders and subscriptions)
-- ============================================
CREATE TABLE IF NOT EXISTS billing (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES accounts(customer_id) ON DELETE CASCADE,
    -- Order-based fields (for product purchases)
    order_id VARCHAR(100) UNIQUE,  -- Added: For order tracking
    product_name VARCHAR(255),      -- Added: Product name
    amount DECIMAL(10,2),           -- Added: Order amount
    -- Subscription-based fields (for recurring plans)
    plan VARCHAR(100),             -- Subscription plan name
    price DECIMAL(10,2),           -- Subscription price
    next_billing_date DATE,         -- Next billing date for subscription
    payment_method VARCHAR(100),    -- Payment method used
    -- Common fields
    status VARCHAR(50) DEFAULT 'active',  -- active, cancelled, failed, paid, pending
    billing_type VARCHAR(50) DEFAULT 'subscription',  -- 'subscription' or 'order'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- FAQ TABLE (No changes needed)
-- ============================================
CREATE TABLE IF NOT EXISTS faqs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    keywords TEXT[],
    priority INTEGER DEFAULT 5,
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================
-- TECHNICAL ISSUES TABLE (No changes needed)
-- ============================================
CREATE TABLE IF NOT EXISTS technical_issues (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES accounts(customer_id) ON DELETE CASCADE,
    issue_type VARCHAR(100),
    description TEXT,
    status VARCHAR(50) DEFAULT 'open',
    solution TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- ============================================
-- INDEXES for Performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_faq_category ON faqs(category);
CREATE INDEX IF NOT EXISTS idx_faq_keywords ON faqs USING GIN(keywords);
CREATE INDEX IF NOT EXISTS idx_faq_active ON faqs(is_active) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_billing_customer ON billing(customer_id);
CREATE INDEX IF NOT EXISTS idx_billing_status ON billing(status);
CREATE INDEX IF NOT EXISTS idx_billing_type ON billing(billing_type);
CREATE INDEX IF NOT EXISTS idx_technical_customer ON technical_issues(customer_id);
CREATE INDEX IF NOT EXISTS idx_technical_status ON technical_issues(status);
CREATE INDEX IF NOT EXISTS idx_accounts_email ON accounts(email);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);

-- ============================================
-- SAMPLE DATA INSERTION
-- ============================================

-- Insert Account Data (10 rows) - Updated with DOB
INSERT INTO accounts (customer_id, email, name, status, created_at, last_login, phone, dob) VALUES
('C001', 'john.doe@example.com', 'John Doe', 'active', '2023-01-15', '2024-01-15', '+1234567890', '1985-05-20'),
('C002', 'jane.smith@example.com', 'Jane Smith', 'active', '2023-06-20', '2024-01-14', '+1234567891', '1990-08-15'),
('C003', 'bob.wilson@example.com', 'Bob Wilson', 'active', '2023-03-10', '2024-01-13', '+1234567892', '1988-12-03'),
('C004', 'alice.johnson@example.com', 'Alice Johnson', 'active', '2023-05-12', '2024-01-12', '+1234567893', '1992-03-25'),
('C005', 'charlie.brown@example.com', 'Charlie Brown', 'active', '2023-07-08', '2024-01-11', '+1234567894', '1987-11-10'),
('C006', 'diana.prince@example.com', 'Diana Prince', 'active', '2023-02-25', '2024-01-10', '+1234567895', '1991-07-18'),
('C007', 'edward.norton@example.com', 'Edward Norton', 'active', '2023-09-14', '2024-01-09', '+1234567896', '1986-09-22'),
('C008', 'fiona.apple@example.com', 'Fiona Apple', 'active', '2023-04-30', '2024-01-08', '+1234567897', '1993-01-14'),
('C009', 'george.lucas@example.com', 'George Lucas', 'active', '2023-11-22', '2024-01-07', '+1234567898', '1984-06-30'),
('C010', 'helen.mirren@example.com', 'Helen Mirren', 'active', '2023-08-05', '2024-01-06', '+1234567899', '1989-04-12')
ON CONFLICT (customer_id) DO NOTHING;

-- Insert Billing Data - Mixed: Subscriptions and Orders
-- Subscription-based billing (5 rows)
INSERT INTO billing (customer_id, plan, price, status, next_billing_date, payment_method, billing_type) VALUES
('C001', 'Premium', 29.99, 'active', '2024-02-15', 'credit_card', 'subscription'),
('C002', 'Basic', 9.99, 'active', '2024-02-20', 'paypal', 'subscription'),
('C003', 'Enterprise', 99.99, 'active', '2024-02-10', 'credit_card', 'subscription'),
('C004', 'Premium', 29.99, 'active', '2024-02-18', 'credit_card', 'subscription'),
('C005', 'Basic', 9.99, 'active', '2024-02-25', 'paypal', 'subscription')
ON CONFLICT DO NOTHING;

-- Order-based billing (5 rows) - Using order_id, product_name, amount
INSERT INTO billing (customer_id, order_id, product_name, amount, status, billing_type, created_at) VALUES
('C006', 'O1001', 'USB Hub', 19.99, 'paid', 'order', '2024-01-10'),
('C007', 'O1002', 'Wireless Mouse', 29.99, 'paid', 'order', '2024-01-09'),
('C008', 'O1003', 'USB Hub', 19.99, 'paid', 'order', '2024-01-08'),
('C009', 'O1004', 'Webcam', 79.00, 'failed', 'order', '2024-01-07'),
('C010', 'O1005', 'Keyboard', 49.99, 'paid', 'order', '2024-01-06')
ON CONFLICT DO NOTHING;

-- Insert FAQ Data (10 rows) - Enhanced with better keywords
INSERT INTO faqs (question, answer, category, keywords, priority) VALUES
('How do I reset my password?', 'Click "Forgot Password" on the login page, enter your email address, and check your email for the reset link. Click the link to create a new password.', 'account', ARRAY['password', 'reset', 'forgot', 'login', 'change password', 'new password'], 9),
('How do I upgrade my plan?', 'Go to Settings > Billing > Upgrade Plan, select your desired plan, and complete the payment. Your new plan will be activated immediately.', 'billing', ARRAY['upgrade', 'plan', 'billing', 'upgrade plan', 'change plan', 'better plan', 'higher plan'], 8),
('The app is running slow, what should I do?', 'Try these steps: 1) Clear your browser cache, 2) Check your internet connection, 3) Refresh the page, 4) Close other browser tabs. If the issue persists, contact support.', 'technical', ARRAY['slow', 'performance', 'lag', 'speed', 'freezing', 'not responding', 'hanging'], 7),
('How do I change my email address?', 'Go to Settings > Account > Email, enter your new email address, and verify it by clicking the confirmation link sent to your new email.', 'account', ARRAY['email', 'change', 'update', 'modify email', 'new email', 'change email'], 6),
('How do I cancel my subscription?', 'Go to Settings > Billing > Cancel Subscription, review the cancellation terms, and confirm your cancellation. Your subscription will remain active until the end of the billing period.', 'billing', ARRAY['cancel', 'cancel subscription', 'cancel my subscription', 'stop subscription', 'end subscription', 'terminate', 'unsubscribe', 'how cancel'], 9),
('I cannot upload files, what is wrong?', 'Check the following: 1) File size limit (max 100MB), 2) File format is supported (PDF, DOCX, JPG, PNG), 3) Your internet connection is stable. If issues persist, try a different browser.', 'technical', ARRAY['upload', 'file', 'error', 'cannot upload', 'upload failed', 'file upload', 'attachment'], 7),
('How do I add team members?', 'Go to Settings > Team > Add Member, enter the email address of the person you want to invite, assign them a role (Admin, Member, Viewer), and send the invitation.', 'account', ARRAY['team', 'member', 'add', 'invite', 'collaborator', 'user', 'share'], 7),
('What payment methods do you accept?', 'We accept the following payment methods: Credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers. All payments are processed securely.', 'billing', ARRAY['payment', 'method', 'credit', 'paypal', 'bank', 'how to pay', 'payment options'], 6),
('How do I export my data?', 'Go to Settings > Data > Export, select your preferred format (CSV, JSON, or Excel), choose the data range, and click Download. The export will be sent to your email.', 'technical', ARRAY['export', 'data', 'download', 'backup', 'save data', 'download data', 'get my data'], 6),
('How do I change my billing address?', 'Go to Settings > Billing > Address, update your billing address, and save the changes. Make sure to update your payment method if needed.', 'billing', ARRAY['billing', 'address', 'change', 'update', 'modify address', 'billing info'], 5)
ON CONFLICT DO NOTHING;

-- Insert Technical Issues Data (10 rows)
INSERT INTO technical_issues (customer_id, issue_type, description, status, solution, created_at) VALUES
('C001', 'login_error', 'Unable to login with correct credentials', 'resolved', 'Cleared cache and reset password', '2024-01-05'),
('C002', 'upload_error', 'File upload failing for large files', 'open', NULL, '2024-01-10'),
('C003', 'performance', 'App running slow on mobile device', 'open', NULL, '2024-01-12'),
('C004', 'api_error', 'API requests timing out', 'resolved', 'Increased timeout settings', '2024-01-08'),
('C005', 'sync_error', 'Data not syncing across devices', 'open', NULL, '2024-01-11'),
('C006', 'display_error', 'UI elements not displaying correctly', 'resolved', 'Cleared browser cache', '2024-01-09'),
('C007', 'notification_error', 'Not receiving email notifications', 'open', NULL, '2024-01-13'),
('C008', 'integration_error', 'Slack integration not working', 'resolved', 'Reconnected integration', '2024-01-07'),
('C009', 'storage_error', 'Cannot access stored files', 'open', NULL, '2024-01-14'),
('C010', 'search_error', 'Search function returning no results', 'resolved', 'Rebuilt search index', '2024-01-06')
ON CONFLICT DO NOTHING;

-- ============================================
-- USEFUL QUERIES FOR TESTING
-- ============================================

-- View all accounts with billing info
-- SELECT a.customer_id, a.name, a.email, a.phone, a.dob, 
--        b.plan, b.price, b.status as billing_status, b.billing_type
-- FROM accounts a
-- LEFT JOIN billing b ON a.customer_id = b.customer_id;

-- View FAQs by category
-- SELECT category, COUNT(*) as count, 
--        array_agg(question) as questions
-- FROM faqs
-- WHERE is_active = TRUE
-- GROUP BY category;

-- View technical issues by status
-- SELECT status, issue_type, COUNT(*) as count
-- FROM technical_issues
-- GROUP BY status, issue_type;
