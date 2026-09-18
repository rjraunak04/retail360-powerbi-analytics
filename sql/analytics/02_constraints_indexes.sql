-- Retail360 Stage 4: star-schema constraints and indexes

ALTER TABLE analytics.fact_sales
    ADD CONSTRAINT fk_sales_channel
        FOREIGN KEY (channel_key) REFERENCES analytics.dim_channel(channel_key),
    ADD CONSTRAINT fk_sales_product
        FOREIGN KEY (product_key) REFERENCES analytics.dim_product(product_key),
    ADD CONSTRAINT fk_sales_order_date
        FOREIGN KEY (order_date_key) REFERENCES analytics.dim_date(date_key),
    ADD CONSTRAINT fk_sales_due_date
        FOREIGN KEY (due_date_key) REFERENCES analytics.dim_date(date_key),
    ADD CONSTRAINT fk_sales_ship_date
        FOREIGN KEY (ship_date_key) REFERENCES analytics.dim_date(date_key),
    ADD CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_key) REFERENCES analytics.dim_customer(customer_key),
    ADD CONSTRAINT fk_sales_reseller
        FOREIGN KEY (reseller_key) REFERENCES analytics.dim_reseller(reseller_key),
    ADD CONSTRAINT fk_sales_employee
        FOREIGN KEY (employee_key) REFERENCES analytics.dim_employee(employee_key),
    ADD CONSTRAINT fk_sales_promotion
        FOREIGN KEY (promotion_key) REFERENCES analytics.dim_promotion(promotion_key),
    ADD CONSTRAINT fk_sales_currency
        FOREIGN KEY (currency_key) REFERENCES analytics.dim_currency(currency_key),
    ADD CONSTRAINT fk_sales_territory
        FOREIGN KEY (sales_territory_key) REFERENCES analytics.dim_sales_territory(sales_territory_key),
    ADD CONSTRAINT fk_sales_geography
        FOREIGN KEY (geography_key) REFERENCES analytics.dim_geography(geography_key);

ALTER TABLE analytics.fact_inventory
    ADD CONSTRAINT fk_inventory_product
        FOREIGN KEY (product_key) REFERENCES analytics.dim_product(product_key),
    ADD CONSTRAINT fk_inventory_date
        FOREIGN KEY (date_key) REFERENCES analytics.dim_date(date_key);

ALTER TABLE analytics.fact_sales
    ADD CONSTRAINT ck_sales_channel_key
        CHECK (channel_key IN (1, 2)),
    ADD CONSTRAINT ck_sales_order_quantity_nonnegative
        CHECK (order_quantity >= 0);

CREATE INDEX ix_fact_sales_order_date
    ON analytics.fact_sales(order_date_key);
CREATE INDEX ix_fact_sales_product
    ON analytics.fact_sales(product_key);
CREATE INDEX ix_fact_sales_channel
    ON analytics.fact_sales(channel_key);
CREATE INDEX ix_fact_sales_customer
    ON analytics.fact_sales(customer_key);
CREATE INDEX ix_fact_sales_reseller
    ON analytics.fact_sales(reseller_key);
CREATE INDEX ix_fact_sales_employee
    ON analytics.fact_sales(employee_key);
CREATE INDEX ix_fact_sales_promotion
    ON analytics.fact_sales(promotion_key);
CREATE INDEX ix_fact_sales_geography
    ON analytics.fact_sales(geography_key);
CREATE INDEX ix_fact_sales_territory
    ON analytics.fact_sales(sales_territory_key);
CREATE INDEX ix_fact_sales_order
    ON analytics.fact_sales(sales_order_number);

CREATE INDEX ix_fact_inventory_date
    ON analytics.fact_inventory(date_key);

ANALYZE analytics.dim_date;
ANALYZE analytics.dim_product;
ANALYZE analytics.dim_customer;
ANALYZE analytics.dim_reseller;
ANALYZE analytics.dim_employee;
ANALYZE analytics.dim_geography;
ANALYZE analytics.dim_sales_territory;
ANALYZE analytics.dim_promotion;
ANALYZE analytics.dim_currency;
ANALYZE analytics.dim_channel;
ANALYZE analytics.fact_sales;
ANALYZE analytics.fact_inventory;
