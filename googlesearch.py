import requests

class GooggleSearch:
    def __init__(self, api_key, engine_id):
        """
        Inicializa una nueva instancia de GoogleSearch.
        
        Esta clase permite realizar peticiones automatizadas a la API de Google
        
        Args:
            api_key (str): Clave API de Google.
            engine_id (str): Identificador del motor de búsqueda personalizado de Google.
        """
        self.api_key = api_key
        self.engine_id = engine_id


    def search(self, query, start_page=1, pages=1, lang="lang_es"):
        """
        Realiza una búsqueda en Google utilizando su API."""

        final_results = []
        results_per_page = 10 # Google muestra por defecto 10 resultados por página
        for page in range(pages):
            # Calculamos el resultado de comienzo de cada página
            start_index = (start_page -1) * results_per_page + 1 + (page * results_per_page )
            url =f"https://www.googleapis.com/customsearch/v1?key={self.api_key}&cx={self.engine_id}&q={query}&start={start_index}&lr={lang}"      
            response = requests.get(url)
            # Comprobamos si la respuesta es correcta
            if response.status_code == 200:
                data = response.json()
                results = data.get("items")
                cresults = self.custom_results(results)
                final_results.extend(cresults)
            else:
                print(f"Error obtenido al consultar la página: {page}: HTTP: {response.status_code}") 
                break # Rompemos la iteración actual
        return final_results

    def custom_results(self, results):
        """ Filtra los resultados de la consulta"""
        custom_results = [] 
        for r in results:
            cresult = {}
            cresult["title"] = r.get("title")
            cresult["description"] = r.get("snippet")
            cresult["link"] = r.get("link")
            custom_results.append(cresult)
        return custom_results
