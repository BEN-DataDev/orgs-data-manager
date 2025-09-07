CREATE TABLE
    abn_data (
        abn text PRIMARY KEY, -- ABN is a unique identifier
        is_current CHAR(1) CHECK (is_current IN ('Y', 'N')),
        replaced_from DATE,
        entity_status TEXT,
        effective_from DATE,
        effective_to DATE,
        entity_type_code TEXT,
        entity_description TEXT,
        acnc_status TEXT,
        acnc_status_from DATE,
        acnc_status_to DATE,
        record_last_updated DATE,
        gst JSONB,
        dgr JSONB,
        main_trading_names JSONB,
        other_trading_names JSONB,
        main_business_physical_address JSONB,
        tax_concession_endorsements JSONB
    );

COPY abn_data
FROM
    '/data/processed/cleaned_register_results_20250802_1336.csv' DELIMITER ',' CSV HEADER NULL '';