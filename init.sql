--
-- PostgreSQL database dump
--


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
-- Name: permission; Type: TABLE; Schema: public; 
--

CREATE TABLE IF NOT EXISTS public.permission (
    id integer NOT NULL,
    name character varying NOT NULL,
    code character varying NOT NULL
);

--
-- Name: permission_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE public.permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE public.permission_id_seq OWNED BY public.permission.id;

--
-- Data for Name: permission; Type: TABLE DATA; Schema: public; 
--

COPY public.permission (id, name, code) FROM stdin;
1	просмотр клиентов	show_client
2	редактирование клиентов	edit_client
3	добавление клиентов	add_client
5	просмотр номеров	show_room
6	редактирование номеров	edit_room
7	удаление номеров	delete_room
8	просмотр категорий	show_category
9	редактирование категорий	edit_category
10	удаление категорий	delete_category
11	просмотр тегов	show_tag
12	редактирование тегов	edit_tag
13	удаление тегов	delete_tag
14	добавление тегов	add_tag
15	добавление номеров	add_room
16	добавление категорий	add_category
17	добавление скидок	add_sale
18	редактирование скидок	edit_sale
19	просмотр скидок	show_sale
20	удаление скидок	delete_sale
21	добавление фотографий	add_photo
22	редактирование фотографий	edit_photo
23	просмотр фотографий	show_photo
24	удаление фотографий	delete_photo
25	добавление групп	add_group
26	редактирование групп	edit_group
27	просмотр гупп	show_group
28	удаление групп	delete_group
29	добавление сотрудников	add_worker
30	редактирование сотрудников	edit_worker
31	просмотр сотрудников	show_worker
32	удаление сотрудников	delete_worker
33	удаление клиентов	delete_client
34	добавление заказов	add_order
35	редактирование заказов	edit_order
36	просмотр заказов	show_order
37	отмена заказов	cancel_order
38	добавление покупок	add_purchase
39	редактирование покупок	edit_purchase
40	отмена покупок	cancel_purchase
41	просмотр покупок	show_purchase
\.

--
-- Name: permission_id_seq; Type: SEQUENCE SET; Schema: public; 
--

SELECT pg_catalog.setval('public.permission_id_seq', 2, true);

--
-- Name: permission permission_code_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_code_key UNIQUE (code);


--
-- Name: permission permission_name_key; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_name_key UNIQUE (name);


--
-- Name: permission permission_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY public.permission
    ADD CONSTRAINT permission_pkey PRIMARY KEY (id);

--
-- PostgreSQL database dump complete
--

