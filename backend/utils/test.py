import camelot
import fitz

path = 'no_header_footer_1.pdf'

tables = camelot.read_pdf(path,pages='all')
print(tables[0])