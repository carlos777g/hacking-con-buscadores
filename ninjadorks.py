from dotenv import load_dotenv, set_key
import os 
from googlesearch import GooggleSearch
from duckducksearch import DuckDuckSearch
import argparse
import sys
from results_parser import ResultsParser
from file_downloader import FileDownloader
from ai_agent import OpenAIGenerator, GPT4AllGenerator, IaAgent
from browserautosearch import BrowserAutoSearch
from smartsearch import SmartSearch

def env_config():
    """Configurar el archivo .env con los valores proporcionados."""
    api_key = input("Introduce tu API KEY de Google: ")
    engine_id = input("Introduce el ID del buscador personalizado de Google: ")
    set_key(".env", "API_KEY_GOOGLE", api_key)
    set_key(".env", "SEARCH_ENGINE_ID", engine_id)


def openai_config():
    """Configura la API KEY de OepnAI en el fichero .env"""
    api_key = input("Introduce la API KEY de OpenAI: ")
    set_key(".env", "OPENAI_API_KEY", api_key)

def load_env(configure_env):
    """Carga las variables de entorno desde el archivo .env."""
    # Comprobamos si existe el fichero .env
    env_exist = os.path.exists(".env")
    if not env_exist or configure_env:
        env_config()
        print("Archivo .env configurado correctamente.\n")
        sys.exit(1)

    # Cargamos las variables en el entorno
    load_dotenv()

    # Leemos la clave API y el ID del buscador
    API_KEY_GOOGLE = os.getenv("API_KEY_GOOGLE")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
    # Descomentar para usar DuckDuckGo:
    #API_KEY_DUCKDUCKGO = os.getenv("API_KEY_DUCKDUCKGO")

    return (API_KEY_GOOGLE, SEARCH_ENGINE_ID)

def main(query, configure_env, start_page, pages, lang, output_json, output_html, download, gen_dork, smartsearch, regex, prompt, model, max_tokens, selenium):
    """Función principal que ejecuta la búsqueda y maneja los resultados."""
    
    if gen_dork:
        # Preguntamos si el usuario quiere usar un modelo local u OpenAI
        respuesta = ""
        while respuesta not in ("y", "yes", "no", "n"):
            respuesta = input("¿Quieres usar GPT-4 de OpenAI? (yes/no): ").lower()
            if respuesta in ("y", "yes"):
                # Comprobamos si está definida la API KEY de OpenAI en el fichero .env
                load_dotenv()
                if not "OPENAI_API_KEY" in os.environ:
                    openai_config()
                    load_dotenv()
                    print("Archivo .env configurado correctamente.\n")
                # Generamos el dork
                open_ai_generator = OpenAIGenerator()
                ia_agent = IaAgent(open_ai_generator)
            elif respuesta in ("n", "no"):
                print("Utilizando gpt4all y ejecutando la generación en local. Puede tardar varios minutos.")
                gpt4all_generator = GPT4AllGenerator()
                ia_agent = IaAgent(gpt4all_generator)
                
        respuesta = ia_agent.generate_gdork(gen_dork)
        print(f"\nResultado:\n{respuesta}")
        sys.exit(1) 

    if query and not selenium:
        API_KEY_GOOGLE, SEARCH_ENGINE_ID = load_env(configure_env=configure_env)
        gsearch = GooggleSearch(API_KEY_GOOGLE, SEARCH_ENGINE_ID)
        resultados = gsearch.search(query,
                                    pages=pages,
                                    start_page=start_page,
                                    lang=lang)
        rparser = ResultsParser(resultados)

        # Mostrar los resultados en línea de consola de comandos
        rparser.mostrar_pantalla()

        if output_html:
            rparser.exportar_html(output_html)

        if output_json:
            rparser.exportar_json(output_json)
        
        if download:
            # Separar las extensiones de los archivos en una lista
            file_types = download.split(",")
            # Nos quedamos unicamente con las urls de los resultados obtenidos
            urls = [resultado['link'] for resultado in resultados]
            fdownloader = FileDownloader("Descargas") # Especificamos la carpeta de destino
            fdownloader.filtrar_descargar_archivos(urls, file_types)

    if selenium:
        browser = BrowserAutoSearch()
        browser.search_google(query=query)
        resultados = browser.google_search_results()
        browser.quit()
        rparser = ResultsParser(resultados)
        # Mostrar los resultados en línea de consola de comandos
        rparser.mostrar_pantalla()
        # Si el usuario ha especificado un fichero de salida, exportamos los resultados a ese fichero
        if output_html:
            rparser.exportar_html(output_html)

        if output_json:
            rparser.exportar_json(output_json)
        
        if download:
            # Separar las extensiones de los archivos en una lista
            file_types = download.split(",")
            # Nos quedamos unicamente con las urls de los resultados obtenidos
            urls = [resultado['link'] for resultado in resultados]
            fdownloader = FileDownloader("Descargas")
            fdownloader.filtrar_descargar_archivos(urls, file_types)

    if smartsearch:
        searcher = SmartSearch(smartsearch)
        if regex:
            resultados = searcher.regex_search(regex)
            print()
            for file, results in resultados.items():
                print(f"Fichero: {file}")
                for r in results:
                    print(f"\t- {r}")
    
        if prompt:
            resultados = searcher.ia_search(prompt, model, max_tokens)
            print()
            for file, results in resultados.items():
                print(f"Fichero: {file}")
                for r in results:
                    print(f"\t- {r}")


    # Descomentar para usar DuckDuckGo
    #gsearch = DuckDuckSearch(API_KEY_DUCKDUCKGO)
    #resultados = gsearch.search(query)
    #print(resultados)

if __name__ == "__main__":
    # Configuraci'on de  los argumentos del programa
    parser = argparse.ArgumentParser(description="1.-Esta herramienta permite realizar Hacking con buscadores de manera automática \n\n2.-También permite realizar busquedas en los ficheros de un directorio (haciendo uso de smartsearch.py).\n\n3.-Puedes buscar en Google o DuckDuckGo (si tienes la API KEY).\n\n4.-Puedes exportar los resultados a un fichero HTML o JSON.\n\n5.-Puedes descargar los archivos que encuentres en los resultados de busqueda.\n\n6.-Puedes usar la IA para generar dorks o buscar en los ficheros de un directorio.\n\n7.-Puedes usar Selenium para realizar la busqueda con un navegador de manera automática.")
    
    parser.add_argument("-q", "--query", type=str,
                        help="Este argumento especifíca el dork que desea buscar.\nEjemplo: -q 'wikipedia'")
    parser.add_argument("-c", "--configure", action="store_true",
                        help="Inicia el proceso de configuración del archivo .env.\nUtiliza esta opción sin otros argumentos para configurar las claves.")
    parser.add_argument("--start-page", type=int, default=1,
                        help="Define la página de inicio del buscador para obtener los resultados.")        
    parser.add_argument("--pages", type=int, default=1,
                        help="Número de páginas de resultados de busqueda.")    
    parser.add_argument("--lang", type=str, default="lang_es",
                        help="Código de idioma para los resultados de búsqueda. Por defecto es 'lang_es' (español).")
    parser.add_argument("--json", type=str,
                        help="Exporta los resultados en formato JSON en el fichero especificado.")
    parser.add_argument("--html", type=str,
                        help="Exporta los resultados a formato HTML en el fichero especificado.")    
    parser.add_argument("--download", type=str, default=None,
                        help="Especifica las extensiones de los archivos que quieres descargar separadas entre coma. Ej: --download 'pdf,doc,sql'"
                        )
    parser.add_argument("-gd", "--generate-dork", type=str,
                        help="Genera una descripción proporcionada por el usuario.\nEj: --generate-dork 'Listado de usuarios y passwords en ficheros de texto'")
    

    parser.add_argument("-s", "--smartsearch", type=str,
                        help="Usa esta opción si quieres usar SmartSearch (herramienta adicional para realizar busquedas en los ficheros de un directorio).\nEj: -s '/ruta/del/directorio'")
    parser.add_argument("-r", "--regex", type=str,
                        help="La expresión regular para realizar la busqueda.")
    parser.add_argument("-p", "--prompt", type=str,
                        help="El prompt para realizar la busqueda con GPT.")
    parser.add_argument("-m", "--model", type=str, default="gpt-3.5-turbo-0125",
                        help="El modelo de OpenAI para realizar la busqueda.")
    parser.add_argument("--max_tokens", type=int, default=100,
                        help="El número máximo de tokens en la predicción/generación.")
    
    parser.add_argument("--selenium", action="store_true", default=False,
                        help="Utiliza Selenium para realizar la búsqueda con un navegador de manera automática.")
    

    args = parser.parse_args()

    print("\n[+] Iniciando la herramienta de busqueda de dorks.\nRecuerda usar el comando -q para realizar una busqueda, -s para usar la herramienta de busqueda en ficheros o -h para ver la ayuda de funcionamiento.\n")
    # Comprobamos si el usuario quiere usar la herramienta de busqueda en ficheros (smartsearch)
    if args.smartsearch:
        if not os.path.isdir(args.smartsearch):
            print("[!] Error: La ruta proporcionada no es un directorio válido.")
            sys.exit(1)
        

    main(query=args.query,
         configure_env=args.configure,
         pages=args.pages,
         start_page=args.start_page,
         lang=args.lang,
         output_html=args.html,
         output_json=args.json,
         download=args.download,
         gen_dork=args.generate_dork,

         smartsearch=args.smartsearch,
         regex=args.regex,
         prompt=args.prompt,
         model=args.model,
         max_tokens=args.max_tokens,

         selenium=args.selenium
         )
        
