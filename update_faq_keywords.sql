-- ============================================
-- UPDATE FAQ KEYWORDS FOR BETTER MATCHING
-- Run this to fix existing FAQ keyword issues
-- ============================================

-- Update "How do I upgrade my plan?" - Remove generic "subscription" keyword
UPDATE faqs 
SET keywords = ARRAY['upgrade', 'plan', 'billing', 'upgrade plan', 'change plan', 'better plan', 'higher plan']
WHERE question = 'How do I upgrade my plan?';

-- Update "How do I cancel my subscription?" - Add more specific keywords and increase priority
UPDATE faqs 
SET 
    keywords = ARRAY['cancel', 'cancel subscription', 'cancel my subscription', 'stop subscription', 'end subscription', 'terminate', 'unsubscribe', 'how cancel'],
    priority = 9
WHERE question = 'How do I cancel my subscription?';

-- Verify the updates
SELECT question, keywords, priority 
FROM faqs 
WHERE question IN ('How do I upgrade my plan?', 'How do I cancel my subscription?')
ORDER BY question;
