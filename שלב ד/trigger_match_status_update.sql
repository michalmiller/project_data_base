-- ============================================================
-- Trigger 1: trg_match_status_update
-- Description: Fires on UPDATE of the match table when status
--              changes. Validates the transition, logs the change,
--              and auto-updates related data (e.g., attendance
--              reset on cancellation).
-- Trigger Type: BEFORE UPDATE (on status column)
-- Elements used: Branching, DML (INSERT), Exception, Records
-- ============================================================

-- Create audit log table for match status changes
CREATE TABLE IF NOT EXISTS match_status_audit (
    audit_id SERIAL PRIMARY KEY,
    match_id INT NOT NULL,
    old_status VARCHAR NOT NULL,
    new_status VARCHAR NOT NULL,
    changed_by VARCHAR DEFAULT CURRENT_USER,
    change_reason VARCHAR,
    changed_at TIMESTAMP DEFAULT NOW()
);

-- Drop existing trigger and function
DROP TRIGGER IF EXISTS trg_match_status_update ON match;
DROP FUNCTION IF EXISTS fn_match_status_update();

-- ============================================================
-- Trigger Function
-- ============================================================
CREATE OR REPLACE FUNCTION fn_match_status_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_valid_transition BOOLEAN := FALSE;
    v_reason VARCHAR;
    v_event_count INT := 0;
BEGIN
    -- Only proceed if status actually changed
    IF OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;
    
    RAISE NOTICE 'Match % status change: % -> %', 
                 NEW.match_id, OLD.status, NEW.status;
    
    -- Validate status transitions with branching
    IF OLD.status = 'Scheduled' THEN
        -- From Scheduled: can go to Finished or Cancelled
        IF NEW.status IN ('Finished', 'Cancelled') THEN
            v_valid_transition := TRUE;
        ELSE
            v_valid_transition := FALSE;
        END IF;
        
    ELSIF OLD.status = 'Finished' THEN
        -- From Finished: can only go to Cancelled (dispute/error)
        IF NEW.status = 'Cancelled' THEN
            v_valid_transition := TRUE;
            v_reason := 'Post-game cancellation (dispute or error)';
        ELSE
            v_valid_transition := FALSE;
        END IF;
        
    ELSIF OLD.status = 'Cancelled' THEN
        -- From Cancelled: can go back to Scheduled (rescheduled)
        IF NEW.status = 'Scheduled' THEN
            v_valid_transition := TRUE;
            v_reason := 'Match rescheduled';
        ELSE
            v_valid_transition := FALSE;
        END IF;
        
    ELSE
        -- Unknown status - allow but log warning
        v_valid_transition := TRUE;
        v_reason := 'Unknown source status: ' || OLD.status;
        RAISE NOTICE 'WARNING: Unknown source status "%" for match %',
                     OLD.status, NEW.match_id;
    END IF;
    
    -- Block invalid transitions
    IF NOT v_valid_transition THEN
        RAISE EXCEPTION 'Invalid status transition: "%" -> "%" for match %. Allowed transitions: Scheduled->(Finished,Cancelled), Finished->(Cancelled), Cancelled->(Scheduled)',
                        OLD.status, NEW.status, NEW.match_id;
    END IF;
    
    -- Apply side effects based on new status
    IF NEW.status = 'Cancelled' THEN
        -- Reset scores to 0 on cancellation
        NEW.home_score := 0;
        NEW.away_score := 0;
        v_reason := COALESCE(v_reason, 'Match cancelled - scores reset');
        
        RAISE NOTICE 'Match % cancelled: scores reset to 0-0', NEW.match_id;
        
    ELSIF NEW.status = 'Finished' THEN
        -- Validate that scores are set
        IF NEW.home_score IS NULL OR NEW.away_score IS NULL THEN
            RAISE EXCEPTION 'Cannot finish match % without valid scores', NEW.match_id;
        END IF;
        
        -- Count match events
        SELECT COUNT(*) INTO v_event_count
        FROM matchevent
        WHERE match_id = NEW.match_id;
        
        IF v_event_count = 0 THEN
            RAISE NOTICE 'WARNING: Match % finished with no recorded events', NEW.match_id;
        ELSE
            RAISE NOTICE 'Match % finished with % events recorded', 
                         NEW.match_id, v_event_count;
        END IF;
        
        v_reason := COALESCE(v_reason, 
                    'Match finished: ' || NEW.home_score || '-' || NEW.away_score ||
                    ' (' || v_event_count || ' events)');
                    
    ELSIF NEW.status = 'Scheduled' THEN
        v_reason := COALESCE(v_reason, 'Match scheduled/rescheduled');
    END IF;
    
    -- DML: Log the status change
    INSERT INTO match_status_audit (match_id, old_status, new_status, change_reason)
    VALUES (NEW.match_id, OLD.status, NEW.status, v_reason);
    
    RETURN NEW;

EXCEPTION
    WHEN RAISE_EXCEPTION THEN
        -- Re-raise our own exceptions
        RAISE;
    WHEN OTHERS THEN
        RAISE NOTICE 'ERROR in trigger fn_match_status_update: %', SQLERRM;
        RAISE;
END;
$$;

-- ============================================================
-- Create the Trigger (BEFORE UPDATE)
-- ============================================================
CREATE TRIGGER trg_match_status_update
    BEFORE UPDATE ON match
    FOR EACH ROW
    WHEN (OLD.status IS DISTINCT FROM NEW.status)
    EXECUTE FUNCTION fn_match_status_update();

-- ============================================================
-- Test the trigger
-- ============================================================

-- Test 1: Valid transition Scheduled -> Finished
SELECT match_id, status, home_score, away_score
FROM match WHERE status = 'Scheduled' LIMIT 1;

UPDATE match
SET status = 'Finished'
WHERE match_id = (SELECT match_id FROM match WHERE status = 'Scheduled' LIMIT 1);

-- Test 2: Valid transition Scheduled -> Cancelled (scores reset)
UPDATE match
SET status = 'Cancelled'
WHERE match_id = (SELECT match_id FROM match WHERE status = 'Scheduled' LIMIT 1);

-- Test 3: Invalid transition (should raise error)
-- UPDATE match SET status = 'Finished' WHERE status = 'Cancelled' LIMIT 1;

-- View the audit log
SELECT * FROM match_status_audit ORDER BY changed_at DESC LIMIT 5;
