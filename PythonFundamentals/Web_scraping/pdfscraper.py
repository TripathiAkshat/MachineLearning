import io
from urllib.request import Request, urlopen
from PyPDF2 import PdfReader

url = 'https://numpy.org/doc/1.18/numpy-user.pdf'

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
remote_file = urlopen(req).read()

memory_file = io.BytesIO(remote_file)
pdf = PdfReader(memory_file)

for page in pdf.pages:
    print(page.extract_text())
