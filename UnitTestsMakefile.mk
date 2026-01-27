all: initial_api core_api module10

initial_api:
	python3 -m unittest tests.unit.initial_api
# 	python3 -m unittest tests.unit.initial_api.test_get_product_lambda   
# 	python3 -m unittest tests.unit.initial_api.test_delete_product_lambda
# 	python3 -m unittest tests.unit.initial_api.test_insert_product_lambda
# 	python3 -m unittest tests.unit.initial_api.test_query_products_lambda
# 	python3 -m unittest tests.unit.initial_api.test_options_lambda

core_api:
	python3 -m unittest tests.unit.core_api.test_options_lambda
	python3 -m unittest tests.unit.core_api.test_get_product_lambda
 	python3 -m unittest tests.unit.core_api.test_insert_product_lambda
# 	python3 -m unittest tests.unit.core_api.test_delete_product_lambda
# 	python3 -m unittest tests.unit.core_api.test_query_products_lambda

module10:
	python3 -m unittest tests.unit.module10.test_products_db_moto
	python3 -m unittest tests.unit.module10.test_products_db_patch
