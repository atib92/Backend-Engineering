-- KEYS[1]: KEY (ratelimit:user:12345)
-- ARGV[1]: CAPACITY (e.g., 100)
-- ARGV[2]: RATE (tokens/sec, e.g., 1.0)
-- ARGV[3]: REQUEST_COST (e.g., 1)
-- ARGV[4]: NOW (current Unix timestamp, e.g., 1678886400.123)
-- ARGV[5]: TTL (optional expiry in seconds, e.g., 1800)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local cost = tonumber(ARGV[3])
local now = tonumber(ARGV[4])
local ttl = tonumber(ARGV[5])

-- 1. LOAD: Retrieve current tokens and last refill timestamp
local stored = redis.call('HMGET', key, 'tokens', 'timestamp')
local current_tokens = tonumber(stored[1])
local last_refill_ts = tonumber(stored[2])

-- Initialize bucket if it doesn't exist. Note we delete keys to manage memory (Think of high cardinality keys like users/ipaddresses etc. Optimization: Do not delete persistant keys like API endpoints.)
if not current_tokens then
    current_tokens = capacity
    last_refill_ts = now
end

-- 2. REFILL: Calculate and add tokens since last check
local time_elapsed = now - last_refill_ts
local tokens_to_add = time_elapsed * rate

local new_tokens = math.min(capacity, current_tokens + tokens_to_add)

-- 3. CONSUME: Check if the request can be allowed
if new_tokens >= cost then
    -- ALLOW: Consume tokens and update the bucket
    local final_tokens = new_tokens - cost
    
    redis.call('HMSET', key, 'tokens', final_tokens, 'timestamp', now)
    redis.call('EXPIRE', key, ttl)
    
    -- Return 1 (Allowed) and the number of tokens remaining
    return {1, final_tokens}
else
    -- BLOCK: Do not update the bucket, request is blocked
    -- Calculate and return the time until the next request is allowed
    -- Tokens needed: cost - new_tokens
    -- Time until allowed: (cost - new_tokens) / rate
    local needed = cost - new_tokens
    local retry_after = math.ceil(needed / rate)

    redis.call('EXPIRE', key, ttl)
    
    -- Return 0 (Blocked) and the calculated Retry-After time
    return {0, retry_after}
end
