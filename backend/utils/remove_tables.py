import fitz
import re
import os
import camelot
import globals
import gc

import warnings

warnings.filterwarnings("ignore", message=".*rmtree.*")

def remove_and_extract_tables(path):
    globals.count+=1
    pdf = fitz.open(path)

    pages_with_table =[]
    table_data = []
    dict_tables = {}

    print(f"#########################################TABLES OF pdf {globals.count}")

    try:
        for i in range(1, len(pdf)):
            try:
                tables_with_lines = camelot.read_pdf(
                    path,
                    pages=str(i),
                    strip_text='\n',
                )

                if tables_with_lines and len(tables_with_lines) > 0:
                    pages_with_table.append(i)
                    table_of_a_page = []

                    for table in tables_with_lines:
                        table_of_a_page.append(table._bbox)
                        table_data.append(table.df)

                    dict_tables[i] = table_of_a_page

                    # Free up camelot objects and memory
                if tables_with_lines:
                    del tables_with_lines
                tables_with_lines = None
                gc.collect()
            except Exception as e:
                print(f"Error processing page {i}: {e}")
                continue

            # Redact tables from the original PDF
        for num_page, table_bboxes in dict_tables.items():
            page = pdf[num_page - 1]
            page_height = page.rect.height

            for x1, y1, x2, y2 in table_bboxes:
                y1_fitz = page_height - y1
                y2_fitz = page_height - y2
                rect = fitz.Rect(x1, y2_fitz, x2, y1_fitz)
                page.add_redact_annot(rect, fill=(1, 1, 1))

            page.apply_redactions()

        # Save output
        out_path = f"table_deleted_{globals.count}.pdf"
        pdf.save(out_path)

        return table_data, out_path
        
    except Exception as e:
        print(f"An error occurred while processing the PDF: {e}")
        return [], None
    
    finally:
        # Ensure PDF is always closed properly
        try:
            pdf.close()
        except:
            pass
        # Force cleanup
        gc.collect()

# def store_table_data(tables_data):
#     table_out_path = f"tables_extracted/tables_data_{globals.count}.pdf"
#     #creating a new pdf file to insert table data 

#     tables_data = [data.to_string(index=False) for data in tables_data]
#     filtered_table_data = []
#     for data in tables_data:
#         cleaned = re.sub(r'\s+', ' ', data)
#         if(len(cleaned) > 20):
#             filtered_table_data.append(data)

#     if(filtered_table_data):
#         try: 
#             #if there are tables present in document then open a pdf
#             file = fitz.open()
#             for data in filtered_table_data:
#                 page = file.new_page()
#                 page.insert_text((72,72),data,fontsize = 12)
#                 file.save(table_out_path)
            
#         finally:
#             file.close()

def store_table_data(tables_data):
    output_dir = "tables_extracted"
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

    table_out_path = os.path.join(output_dir, f"tables_data_{globals.count}.pdf")

    # Convert tables to string and clean them
    tables_data = [data.to_string(index=False) for data in tables_data]
    filtered_table_data = []
    for data in tables_data:
        cleaned = re.sub(r'\s+', ' ', data)
        if len(cleaned) > 20:
            filtered_table_data.append(cleaned)

    # Only create PDF if there is table content
    if filtered_table_data:
        file = fitz.open()  # Create new PDF
        try:
            for data in filtered_table_data:
                page = file.new_page()
                page.insert_text((72, 72), data, fontsize=12)
            file.save(table_out_path)
        except Exception as e:
            print(f"Error occurred while saving PDF: {e}")
        finally:
            try:
                file.close()
            except:
                pass
            # Force cleanup after file operations
            gc.collect()
