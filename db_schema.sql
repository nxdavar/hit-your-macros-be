--
-- PostgreSQL database dump
--

-- Dumped from database version 14.12 (Homebrew)
-- Dumped by pg_dump version 14.13 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: hym_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);




--
-- Name: menu_item; Type: TABLE; Schema: public; Owner: hym_user
--

CREATE TABLE public.menu_item (
    menu_item_id uuid NOT NULL,
    restaurant_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description character varying,
    price numeric(10,2),
    kcal double precision NOT NULL,
    kcal_from_fat double precision,
    grams_protein double precision,
    grams_carbs double precision,
    grams_dietary_fiber double precision,
    grams_total_sugar double precision,
    grams_added_sugar double precision,
    grams_saturated_fat double precision,
    grams_trans_fat double precision,
    grams_monounsat_fat double precision,
    grams_polyunsat_fat double precision,
    mg_cholesterol double precision,
    mg_sodium double precision,
    ingredients character varying,
    allergens character varying,
    is_breakfast boolean,
    is_dessert boolean,
    is_side_condiment boolean,
    is_add_on boolean,
    is_vegetarian boolean,
    contains_caffeine boolean,
    contains_alcohol boolean,
    contains_seafood boolean,
    is_kids_meal boolean,
    is_beverage boolean,
    is_dairy_free boolean,
    is_pescatarian boolean,
    is_vegan boolean,
    is_gluten_free boolean,
    is_keto boolean,
    created_at character varying,
    updated_at character varying,
    grams_total_fat double precision,
    serving_size_oz double precision,
    mg_calcium double precision,
    mg_potassium double precision,
    mg_iron double precision,
    mcg_vitamin_a double precision,
    mg_vitamin_c double precision
);



--
-- Name: menu_item_filter; Type: TABLE; Schema: public; Owner: hym_user
--

CREATE TABLE public.menu_item_filter (
    filter_id uuid NOT NULL,
    menu_item_id uuid NOT NULL,
    filter_name character varying(100) NOT NULL,
    filter_value boolean NOT NULL
);



--
-- Name: restaurant; Type: TABLE; Schema: public; Owner: hym_user
--

CREATE TABLE public.restaurant (
    restaurant_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    address character varying(255),
    zipcode character varying(10),
    latitude double precision,
    longitude double precision,
    cuisine character varying(100),
    open_hours json,
    breakfast_start_time time without time zone,
    breakfast_end_time time without time zone,
    customizable boolean,
    open_now boolean,
    created_at character varying,
    updated_at character varying
);




--
-- Name: zipcode_geolocation; Type: TABLE; Schema: public; Owner: hym_user
--

CREATE TABLE public.zipcode_geolocation (
    zipcode character varying(10) NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL
);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: hym_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: menu_item_filter menu_item_filter_pkey; Type: CONSTRAINT; Schema: public; Owner: hym_user
--

ALTER TABLE ONLY public.menu_item_filter
    ADD CONSTRAINT menu_item_filter_pkey PRIMARY KEY (filter_id);


--
-- Name: menu_item menu_item_pkey; Type: CONSTRAINT; Schema: public; Owner: hym_user
--

ALTER TABLE ONLY public.menu_item
    ADD CONSTRAINT menu_item_pkey PRIMARY KEY (menu_item_id);


--
-- Name: restaurant restaurant_pkey; Type: CONSTRAINT; Schema: public; Owner: hym_user
--

ALTER TABLE ONLY public.restaurant
    ADD CONSTRAINT restaurant_pkey PRIMARY KEY (restaurant_id);


--
-- Name: zipcode_geolocation zipcode_geolocation_pkey; Type: CONSTRAINT; Schema: public; Owner: hym_user
--

ALTER TABLE ONLY public.zipcode_geolocation
    ADD CONSTRAINT zipcode_geolocation_pkey PRIMARY KEY (zipcode);


--
-- Name: menu_item_filter menu_item_filter_menu_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hym_user
--

ALTER TABLE ONLY public.menu_item_filter
    ADD CONSTRAINT menu_item_filter_menu_item_id_fkey FOREIGN KEY (menu_item_id) REFERENCES public.menu_item(menu_item_id) ON DELETE CASCADE;


--
-- Name: menu_item menu_item_restaurant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: hym_user
--

ALTER TABLE ONLY public.menu_item
    ADD CONSTRAINT menu_item_restaurant_id_fkey FOREIGN KEY (restaurant_id) REFERENCES public.restaurant(restaurant_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--
