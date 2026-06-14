ALTER TABLE branch
ADD COLUMN IF NOT EXISTS store_id INT;

UPDATE branch
SET store_id = (
    SELECT MIN(store_id)
    FROM clothingstore
)
WHERE store_id IS NULL;

ALTER TABLE branch
ADD CONSTRAINT fk_branch_store
FOREIGN KEY (store_id)
REFERENCES clothingstore(store_id);