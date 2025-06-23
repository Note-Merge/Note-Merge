import fitz
import re
import camelot
import globals

def remove_and_extract_tables(path):
    globals.count+=1
    pdf = fitz.open(path)
    print(len(pdf))

    pages_with_table =[]
    table_data = []

    dict_tables = {}

    print(f"#########################################TABLES OF pdf {globals.count}")

    for i in range(1,len(pdf)):
        tables_with_lines = camelot.read_pdf(path,pages=f"{i}")
        if(tables_with_lines):
            pages_with_table.append(i)
            
    for i in pages_with_table:
        tables = camelot.read_pdf(path,pages=f"{i}")
        tables_of_a_page = []

        for table in tables:
            tables_of_a_page.append(table._bbox)
            print(table.df)
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
    return table_data,out_path      


def store_table_data(tables_data):
    table_out_path = f"tables_extracted/tables_data_{globals.count}.pdf"
    #creating a new pdf file to insert table data 

    tables_data = [data.to_string(index=False) for data in tables_data]
    filtered_table_data = []
    for data in tables_data:
        cleaned = re.sub(r'\s+', ' ', data)
        if(len(cleaned) > 20):
            filtered_table_data.append(data)

    if(filtered_table_data):
        try: 
            #if there are tables present in document then open a pdf
            file = fitz.open()
            for data in filtered_table_data:
                page = file.new_page()
                page.insert_text((72,72),data,fontsize = 12)
                file.save(table_out_path)
            
        finally:
            file.close()