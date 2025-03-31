_L='yellow'
_K='magenta'
_J='Parameter'
_I='Content-Type'
_H='Referer'
_G='Accept'
_F='User-Agent'
_E='GET'
_D='json'
_C='http'
_B='blue'
_A='green'
import json,re,requests
from urllib.parse import urlparse,parse_qs,urljoin
from bs4 import BeautifulSoup
import time,random
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import sys,os
from rich.text import Text
import webbrowser
console=Console()
ua=UserAgent()
class APIScanner:
	def __init__(A,target_url,max_threads=5,timeout=15):B=target_url;A.target_url=B if B.startswith(_C)else f"https://{B}";A.base_domain=urlparse(A.target_url).netloc;A.session=requests.Session();A.session.headers.update({_F:ua.random,_G:'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Language':'en-US,en;q=0.5',_H:A.target_url,'DNT':'1'});A.timeout=timeout;A.max_threads=max_threads;A.discovered_endpoints=set();A.js_files=set();A.api_patterns=['(https?://[^"\\\'\\s]+?/api/[^"\\\'\\s]+)','(https?://[^"\\\'\\s]+?/v[0-9]+/[^"\\\'\\s]+)','(https?://[^"\\\'\\s]+?/graphql[^"\\\'\\s])','fetch\\(["\\\'][^"\\\']+["\\\']\\)','window\\.location\\.href\\s*=\\s*["\\\'][^"\\\']+["\\\']','https?://[^"\\\'\\s]+/rest/[^"\\\'\\s]+','https?://[^"\\\'\\s]+/json/[^"\\\'\\s]+','https?://[^"\\\'\\s]+/data/[^"\\\'\\s]+'];A.interesting_keys=['token','auth','key','secret','password','user','id','email'];A.blacklist=['google','facebook','twitter','gstatic','cloudflare']
	def animate_text(B,text,color=_A):A=Text();A.append(text,style=color);console.print(A)
	def clear_screen(A):os.system('cls'if os.name=='nt'else'clear')
	def show_banner(D):webbrowser.open('https://t.me/swarehackteam');A='\n        \n   ▄████████  ▄█     █▄     ▄████████    ▄████████    ▄████████ \n  ███    ███ ███     ███   ███    ███   ███    ███   ███    ███ \n  ███    █▀  ███     ███   ███    ███   ███    ███   ███    █▀  \n  ███        ███     ███   ███    ███  ▄███▄▄▄▄██▀  ▄███▄▄▄     \n▀███████████ ███     ███ ▀███████████ ▀▀███▀▀▀▀▀   ▀▀███▀▀▀     \n         ███ ███     ███   ███    ███ ▀███████████   ███    █▄  \n   ▄█    ███ ███ ▄█▄ ███   ███    ███   ███    ███   ███    ███ \n ▄████████▀   ▀███▀███▀    ███    █▀    ███    ███   ██████████ \n                                        ███    ███              \n\n';B=Text('Sware API Pull Tool',style='bold blue');C=Text('Sware Hack Team',style='bold red');console.print(Panel.fit(Text(A,style='red'),title=B,subtitle=C,border_style=_B))
	def random_delay(A):time.sleep(random.uniform(.5,2.5))
	def is_valid_url(B,url):
		A=False
		if not url.startswith(_C):return A
		if any(A in url for A in B.blacklist):return A
		return True
	def normalize_url(B,url):
		A=url
		if A.startswith('//'):return f"https:{A}"
		elif A.startswith('/'):return f"https://{B.base_domain}{A}"
		return A
	def scan_page(C,url):
		A=url
		try:
			C.random_delay()
			with console.status(f"[cyan]Scanning: {A}[/cyan]",spinner='dots'):
				B=C.session.get(A,timeout=C.timeout)
				if B.status_code==200:
					D=B.headers.get(_I,'')
					if'text/html'in D:C.parse_html(B.text,A)
					elif'javascript'in D:C.parse_js(B.text,A)
					elif _D in D:C.analyze_api_response(B,A)
					elif'xml'in D:C.parse_xml(B.text,A)
				elif B.status_code in[403,401]:console.print(f"[red][!] Access Denied: {A} (Status: {B.status_code})[/red]")
				elif B.status_code==404:console.print(f"[yellow][-] Not Found: {A}[/yellow]")
		except requests.exceptions.RequestException as E:console.print(f"[red][!] Request error ({A}): {str(E)}[/red]")
		except Exception as E:console.print(f"[red][!] General error ({A}): {str(E)}[/red]")
	def parse_html(A,html,page_url):
		I='src';E=BeautifulSoup(html,'html.parser')
		for C in E.find_all('script'):
			if C.get(I):
				D=A.normalize_url(C[I])
				if D not in A.js_files and A.is_valid_url(D):A.js_files.add(D);console.print(f"[cyan][*] JS File Discovered: {D}[/cyan]")
			if C.string:A.search_in_text(C.string,page_url)
		for J in E.find_all(['a','link']):
			F=J.get('href')
			if F:
				B=A.normalize_url(F)
				if A.is_valid_url(B):A.search_in_url(B)
		for G in E.find_all('form'):
			H=G.get('action')
			if H:
				B=A.normalize_url(H)
				if A.is_valid_url(B):A.search_in_url(B);A.analyze_form(G,B)
	def analyze_form(E,form,action_url):
		A=Table(title=f"Form Analysis: {action_url}");A.add_column(_J,style=_K);A.add_column('Type',style=_B)
		for B in form.find_all('input'):C=B.get('name','unnamed');D=B.get('type','text');A.add_row(C,D)
		console.print(A)
	def parse_js(A,js_content,js_url):
		B=js_content;A.search_in_text(B,js_url);D=re.findall('__webpack_require__\\(["\\\'][^"\\\']+["\\\']',B)
		for E in D:
			C=A.normalize_url(E)
			if A.is_valid_url(C):A.scan_page(C)
	def parse_xml(C,xml_content,xml_url):
		B=xml_url
		try:
			D=ET.fromstring(xml_content)
			for A in D.iter():
				if A.text and _C in A.text:C.search_in_text(A.text,B)
		except ET.ParseError as E:console.print(f"[yellow][-] XML parse error ({B}): {str(E)}[/yellow]")
	def search_in_text(A,text,source_url):
		for D in A.api_patterns:
			E=re.finditer(D,text)
			for C in E:
				F=C.group(1)if len(C.groups())>0 else C.group(0);B=A.normalize_url(F)
				if A.is_valid_url(B)and B not in A.discovered_endpoints:A.discovered_endpoints.add(B);console.print(f"[green][+] API Endpoint Found: {B} (Source: {source_url})[/green]");A.analyze_api_endpoint(B)
	def search_in_url(B,url):
		A=url
		if any(B in A.lower()for B in['api','v1','v2','graphql','rest',_D]):
			if A not in B.discovered_endpoints and B.is_valid_url(A):B.discovered_endpoints.add(A);console.print(f"[green][+] API Endpoint Found in URL: {A}[/green]");B.analyze_api_endpoint(A)
	def analyze_api_endpoint(D,api_url):
		A=api_url
		try:
			F=urlparse(A);E=parse_qs(F.query)
			if E:
				B=Table(title=f"Query Parameters: {A}");B.add_column(_J,style=_B);B.add_column('Value(s)',style=_A)
				for(C,G)in E.items():
					B.add_row(C,', '.join(G))
					if any(A in C.lower()for A in D.interesting_keys):console.print(f"[red][!] Interesting parameter found: {C}[/red]")
				console.print(B)
			H=[_E,'POST','PUT','DELETE','PATCH']
			for I in H:D.test_api_endpoint(A,I)
		except Exception as J:console.print(f"[red][!] API analysis error ({A}): {str(J)}[/red]")
	def test_api_endpoint(A,api_url,method=_E):
		D=method;C=api_url
		try:
			A.random_delay();F={_F:ua.random,_G:'application/json, text/plain, */*','Origin':f"https://{A.base_domain}",_H:A.target_url}
			with console.status(f"[cyan]Sending {D} request: {C}[/cyan]",spinner='dots'):
				if D==_E:B=A.session.get(C,headers=F,timeout=A.timeout)
				elif D=='POST':B=A.session.post(C,headers=F,json={},timeout=A.timeout)
				else:B=A.session.request(D,C,headers=F,timeout=A.timeout)
				console.print(f"\n[cyan][*] {D} {C} (Status: {B.status_code})[/cyan]");J=['Authorization','X-API-KEY','X-CSRF-TOKEN','Set-Cookie'];E=Table(title='Interesting Headers');E.add_column('Header',style=_K);E.add_column('Value',style=_L)
				for(H,K)in B.headers.items():
					if any(A.lower()in H.lower()for A in J):E.add_row(H,K)
				if E.rows:console.print(E)
				if B.text:
					L=B.headers.get(_I,'')
					if _D in L:
						try:I=B.json();console.print('[green][i] JSON Response:[/green]');console.print(json.dumps(I,indent=2)[:1000]);A.find_interesting_data(I)
						except ValueError:console.print('[yellow][i] Non-JSON response:[/yellow]');console.print(B.text[:500])
					else:console.print('[yellow][i] Response:[/yellow]');console.print(B.text[:500])
		except requests.exceptions.RequestException as G:console.print(f"[red][!] {D} request error ({C}): {str(G)}[/red]")
		except Exception as G:console.print(f"[red][!] General error ({C}): {str(G)}[/red]")
	def find_interesting_data(B,data,path=''):
		C=path;A=data
		if isinstance(A,dict):
			for(D,E)in A.items():
				F=f"{C}.{D}"if C else D
				if isinstance(E,(dict,list)):B.find_interesting_data(E,F)
				elif any(A in D.lower()for A in B.interesting_keys):console.print(f"[red][!] Interesting data found: {F} = {str(E)[:100]}[/red]")
		elif isinstance(A,list):
			for(G,H)in enumerate(A):B.find_interesting_data(H,f"{C}[{G}]")
	def analyze_api_response(C,response,url):
		A=response
		try:B=A.json();console.print('[green][i] API Response Analysis:[/green]');console.print(json.dumps(B,indent=2)[:1000]);C.find_interesting_data(B)
		except ValueError:console.print('[yellow][i] Non-JSON API response:[/yellow]');console.print(A.text[:500])
	def start_scan(A):
		A.animate_text('\nStarting a scan for the target site.','Red');A.animate_text(f"[*] Target: {A.target_url}",_L);A.scan_page(A.target_url)
		with ThreadPoolExecutor(max_workers=A.max_threads)as B:B.map(A.scan_page,A.js_files)
		with ThreadPoolExecutor(max_workers=A.max_threads)as B:B.map(A.analyze_api_endpoint,A.discovered_endpoints)
		A.animate_text('\n ====== Scan Completed ======',_B);A.animate_text(f"[+] Total {len(A.discovered_endpoints)} API endpoints found",_A);A.animate_text(f"[+] Total {len(A.js_files)} JS files analyzed",_A)
def main():
	A=APIScanner('');A.show_banner()
	def D(sig,frame):print('\nExiting...');sys.exit(0)
	import signal as B;B.signal(B.SIGINT,D)
	while True:
		A.clear_screen();A.show_banner();console.print('\n[red] ====== Welcome To API Pull Tool ======[/red]');console.print('[yellow] Telegram > @swarehackteam[/yellow]');console.print('[yellow] DEV > @spyizxa[/yellow]');C=console.input("\n[bold] Enter target website URL (or 'q' to quit): [/bold]").strip()
		if C.lower()=='q':break
		E=5;F=15;A=APIScanner(C,max_threads=E,timeout=F);A.start_scan();input('\nScan completed. Press Enter to continue...')
if __name__=='__main__':main()