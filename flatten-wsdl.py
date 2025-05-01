import sys
import os
import requests
from lxml import etree
from urllib.parse import urljoin

def download_and_flatten_wsdl(wsdl_url, output_file='flattened.wsdl'):
    downloaded = {}

    def download_recursive(url):
        if url in downloaded:
            return downloaded[url]

        response = requests.get(url)
        response.raise_for_status()
        content = response.content
        tree = etree.XML(content)

        for element in tree.xpath('//*[local-name()="import" or local-name()="include"]'):
            location = element.get("schemaLocation") or element.get("location")
            if location:
                full_url = urljoin(url, location)
                child_tree = download_recursive(full_url)
                parent = element.getparent()
                parent.remove(element)
                for child in child_tree.getroot():
                    parent.append(child)

        downloaded[url] = etree.ElementTree(tree)
        return downloaded[url]

    root_tree = download_recursive(wsdl_url)
    root_tree.write(output_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
    print(f'Flattened WSDL saved to: {output_file}')

# Entry point
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python flatten_wsdl.py <WSDL_URL> [output_file]")
        sys.exit(1)

    wsdl_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'flattened.wsdl'
    download_and_flatten_wsdl(wsdl_url, output_file)
