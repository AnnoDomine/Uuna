SELECT version FROM registry.builds WHERE id < (SELECT id FROM registry.builds WHERE version = ?) ORDER BY id DESC LIMIT 1;
