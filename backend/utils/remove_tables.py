import fitz
import camelot
import globals

def remove_and_extract_tables(path):
    globals.count+=1
    pdf = fitz.open(path)
    print(len(pdf))

    pages_with_table =[]
    table_data = []

    dict_tables = {}


    for i in range(1,len(pdf)):
        tables = camelot.read_pdf(path,pages=f"{i}")
        if(tables):
            pages_with_table.append(i)
            
    for i in pages_with_table:
        tables = camelot.read_pdf(path,pages=f"{i}")
        tables_of_a_page = []

        for table in tables:
            tables_of_a_page.append(table._bbox)
            table_data.append(table.df)
        dict_tables[i] = tables_of_a_page
    
        for num_page, tables in dict_tables.items():
            page = pdf[num_page -1]
            page_height = page.rect.height

            for x1, y1, x2, y2 in tables:
                # Convert Camelot bbox to fitz coordinates (top-left origin)
                y1_fitz = page_height - y1
                y2_fitz = page_height - y2
                rect = fitz.Rect(x1, y2_fitz, x2, y1_fitz)

                # Redact the region (white fill)
                page.add_redact_annot(rect, fill=(1, 1, 1))

            # Apply all redactions after adding them
            page.apply_redactions()

    # Save result
    out_path = f"table_deleted_{globals.count}.pdf"
    pdf.save(out_path) 
    pdf.close()
    return dict_tables,out_path      