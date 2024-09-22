# external imports:
import importlib


# panda_express_menu_item_mapping


def get_restaurant_module(res_name: str):
    module_name = f"data.mapping.{res_name}_header_to_db"
    try:
        module = importlib.import_module(module_name)
        return module
    except ImportError:
        print(f"Module for {res_name} not found.")
        return None


def get_function_from_module(module, attr_name):
    try:
        func = getattr(module, attr_name)
        return func
    except AttributeError:
        print(f"Function {attr_name} not found in module {module.__name__}")
        return None
