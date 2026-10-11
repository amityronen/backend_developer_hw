CREATE ROLE catalog_ro LOGIN PASSWORD :'catalog_pw';
CREATE ROLE admin_rw   LOGIN PASSWORD :'admin_pw';

GRANT CONNECT ON DATABASE melon TO catalog_ro, admin_rw;
GRANT USAGE ON SCHEMA public TO catalog_ro, admin_rw;

GRANT SELECT ON items TO catalog_ro;
GRANT SELECT, INSERT, UPDATE, DELETE ON items, admin_users, audit_log TO admin_rw;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin_rw;
