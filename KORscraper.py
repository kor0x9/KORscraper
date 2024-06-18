import os
import ctypes
from ctypes import wintypes
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style
import time

init()

session = requests.Session()

def title(titre):
    os.system(f'title {titre}')
    
title('KORscraper')

def resize_terminal(width, height):
    kernel32 = ctypes.WinDLL('kernel32')
    hStdOut = kernel32.GetStdHandle(-11)
    
    # Redimensionner le tampon de l'écran
    kernel32.SetConsoleScreenBufferSize(hStdOut, wintypes._COORD(width, height))
    
    # Redimensionner la fenêtre de la console
    rect = wintypes.SMALL_RECT(0, 0, width - 1, height - 1)
    kernel32.SetConsoleWindowInfo(hStdOut, ctypes.c_bool(True), ctypes.byref(rect))

resize_terminal(120, 50)

def banner():
    banner="""
                                                                                \`*-.                   
                                                                               )  _`-.                 
                                                                              .  : `. .               
                                                                              : _   '  \              
                                                                              ; *` _.   `*-._          
                                                                               `-.-'          `-.      
                                                                                 ;       `       `.    
                                                                                 :.       .        \   
                                                                                 . \  .   :   .-'   .  
                                                                                 '  `+.;  ;  '      :  
                                                                                 :  '  |    ;       ;-.
                                                                                 ; '   : :`-:     _.`* ;
                                                                              .*' /  .*' ; .*`- +'  `*'
                                                                              `*-*   `*-*  `*-*
"""
    print(Fore.RED + banner)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def download_resource(url, base_url, output_directory):
    try:
        if url.startswith('/'):
            url = urljoin(base_url, url)
        
        filename = os.path.join(output_directory, os.path.basename(urlparse(url).path))
        
        response = session.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            return os.path.basename(filename)
        else:
            return f"[x] : {os.path.basename(filename)}"
    except Exception as e:
        return f"[x] : {url}"

def format_url(url):
    if not url.startswith('http'):
        url = 'https://' + url
    return url

def scrap_website():
    try:
        clear_console()
        
        banner()
        url_input = input("URL to scrape : ").strip()
        url = format_url(url_input)
        clear_console()
        print(f"Scraping: {url}")
        
        base_url = urlparse(url).scheme + '://' + urlparse(url).netloc
        
        banner()
        output_filename = input("HTML output : ").strip()
        clear_console()
        banner()
        print(f"Url: {url}")
        print(f"Output: {output_filename}")
        time.sleep(2.5)
        clear_console()
        print("Launching...")
        time.sleep(1)
        clear_console()
        
        output_file = output_filename + ".html"
        output_folder = output_filename + "_files"

        current_directory = os.getcwd()
        
        output_path = os.path.join(current_directory, output_file)
        output_folder_path = os.path.join(current_directory, output_folder)
        
        os.makedirs(output_folder_path, exist_ok=True)
        
        response = session.get(url)
        if response.status_code == 200:
            html_content = response.content
            
            with open(output_path, 'wb') as file:
                file.write(html_content)
            
            print(Fore.GREEN + f"HTML generated : {output_path}")
            
            def process_content(content, base_url, output_directory, current_depth):
                soup = BeautifulSoup(content, 'html.parser')

                resource_tasks = []
                with ThreadPoolExecutor(max_workers=10) as executor:
                    for tag in soup.find_all(['img', 'script', 'link']):
                        if tag.name == 'img' and tag.has_attr('src'):
                            url = tag['src']
                            if url.startswith('/'):
                                url = urljoin(base_url, url)
                            resource_tasks.append(executor.submit(download_resource, url, base_url, output_folder_path))
                        elif tag.name == 'script' and tag.has_attr('src'):
                            url = tag['src']
                            if url.startswith('/'):
                                url = urljoin(base_url, url)
                            resource_tasks.append(executor.submit(download_resource, url, base_url, output_folder_path))
                        elif tag.name == 'link' and tag.has_attr('href') and tag.get('rel') == ['stylesheet']:
                            url = tag['href']
                            if url.startswith('/'):
                                url = urljoin(base_url, url)
                            resource_tasks.append(executor.submit(download_resource, url, base_url, output_folder_path))
                    
                    for task in as_completed(resource_tasks):
                        filename = task.result()
                        if filename:
                            if filename.startswith('[x]'):
                                print(Fore.RED + f"{filename}")
                            else:
                                print(Fore.BLUE + f"[+] {filename}")

                for tag in soup.find_all(['a', 'img', 'script', 'link'], href=True):
                    if tag['href'].startswith('/') or tag['href'].startswith('./'):
                        tag['href'] = urljoin(base_url, tag['href'])

                for tag in soup.find_all(['a', 'img', 'script', 'link'], href=True):
                    if tag['href'].startswith(base_url):
                        try:
                            response = session.get(tag['href'])
                            if response.status_code == 200:
                                process_content(response.content, base_url, output_folder_path, current_depth + 1)
                        except Exception as e:
                            print(Fore.RED + f"[x] : Error retrieving {tag['href']}: {e}")

                return soup.prettify()

            html_content = process_content(html_content, base_url, output_folder_path, 0)
            
            with open(output_path, 'wb') as file:
                file.write(html_content.encode('utf-8'))
            
            print(Fore.BLUE + f"Website scraped to: {output_path}")
        else:
            print(Fore.RED + f"Error {response.status_code} retrieving URL {url}.")
    
    except Exception as e:
        print(Fore.RED + f"Error scraping website: {e}")

def main():
    try:
        clear_console()
        print(Fore.RED + "KOR made this")
        time.sleep(3)
        scrap_website()
    except KeyboardInterrupt:
        print(Fore.RED + "\nOperation cancelled by you.")
    except Exception as e:
        print(Fore.RED + f"General error : {e}")

if __name__ == "__main__":
    main()
