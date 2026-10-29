class PluginNotFoundError(Exception):
    pass

class Plugin:
    def execute(self, data):
        raise NotImplementedError("This method should be implemented in sub[3D[K
subclasses")

class UpperCasePlugin(Plugin):
    def execute(self, data):
        return data.upper()

class ReversePlugin(Plugin):
    def execute(self, data):
        return data[::-1]

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, name, plugin):
        if name in self.plugins:
            raise ValueError(f"Plugin with name '{name}' already exists")
        self.plugins[name] = plugin

    def run_plugin(self, name, data):
        if name not in self.plugins:
            raise PluginNotFoundError(f"Plugin '{name}' not found")
        return self.plugins[name].execute(data)

# Создание экземпляра менеджера
manager = PluginManager()

# Регистрация плагинов
manager.register_plugin('upper_case', UpperCasePlugin())
manager.register_plugin('reverse', ReversePlugin())

# Запуск плагинов
result_upper = manager.run_plugin('upper_case', 'hello')
result_reverse = manager.run_plugin('reverse', 'world')

# Попытка запустить несуществующий плагин
try:
    result_unknown = manager.run_plugin('unknown', 'test')
except PluginNotFoundError as e:
    print(e)