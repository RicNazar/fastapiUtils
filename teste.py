from sqlalchemy import types
import inspect

def listar_tipos_sqlalchemy():
    lista_tipos = []

    for _, cls in inspect.getmembers(types, inspect.isclass):
        if issubclass(cls, types.TypeEngine) and cls is not types.TypeEngine:
            # Skip TypeDecorator subclasses (require 'impl')
            if issubclass(cls, getattr(types, "TypeDecorator", object)):
                continue
            try:
                # tenta instanciar sem argumentos
                obj = cls()
            except TypeError:
                # se precisa de argumentos, tenta parâmetros comuns
                try:
                    if 'length' in cls.__init__.__code__.co_varnames:
                        obj = cls(10)
                    elif 'precision' in cls.__init__.__code__.co_varnames:
                        obj = cls(10, 2)
                    else:
                        obj = cls()
                except Exception:
                    continue
            try:
                lista_tipos.append(str(obj))
            except Exception:
                pass

    # remove duplicados e ordena
    lista_tipos = sorted(set(lista_tipos))
    return lista_tipos

if __name__ == "__main__":
    tipos = listar_tipos_sqlalchemy()
    for t in tipos:
        print(t)
