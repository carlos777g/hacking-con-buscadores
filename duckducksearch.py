import requests
from serpapi import GoogleSearch

class DuckDuckSearch:
    def __init__(self, api_key):
        """
        Inicializa una nueva instancia de DuckDuckSearch.

        Esta clase permite realizar peticiones automatizadas a la API de DuckDuckGo.

        Args:
        api_key (str): Clave API de DuckDuckGo.
        engine (str): Identificador del motor de búsqueda personalizado de DuckDuckGo.            
        """
        self.api_key = api_key

    
    def search(self, query, start_page=1, pages=1):
        """
        Realiza una búsqueda en DuckDuckGo utilizando su API.
        """
        final_results = []
        results_per_page = 10 # DuckDuckGo muestra por defecto 10 resultados por página
        for page in range(pages):
            # Calculamos el resultado de comienzo de cada página
            start_index = (start_page - 1) * results_per_page + 1 + (page * results_per_page)
            
            # Creamos el diccionario de parámetros para la búsqueda
            params = {
                    "q" : query,
                    "api_key" : self.api_key,
                    "start" : start_index,
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            # Comprobamos si la respuesta es correcta
            if results["search_metadata"]["status"] == "Success":
                organic_results = results["organic_results"]
                cresults = self.custom_results(organic_results)
                final_results.extend(cresults)
            else:
                print(f"Error obtenido al consultar la página: {page}: HTTP: {results['search_metadata']['status']}")
                break # Rompemos la iteración actual
        return final_results

    
    def custom_results(self, results):
        """ Filtra los resultados de la consulta"""
        custom_results = []
        for r in results:
            cresult = {}
            cresult["title"] = r.get("title")
            cresult["description"] = r.get("about_this_result",{}).get("source",{}).get("description")
            cresult["link"] = r.get("link") 
            custom_results.append(cresult)
        return custom_results       




