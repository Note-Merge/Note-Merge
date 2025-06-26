# from clustering import group_sentences
# import os
# import json
# from fpdf import FPDF

# from sentence_transformers import SentenceTransformer,util
# from collections import defaultdict

# #initialize model
# model = SentenceTransformer('all-mpnet-base-v2')

# grouped1, topic_labels1 = group_sentences("docu.pdf",contains_header= True,contains_footer =False,output_prefix="output1")
# grouped2, topic_labels2 = group_sentences("docu2.pdf",contains_header = True,contains_footer = False,output_prefix="output2")

# def get_topic_embeddings(grouped):
#     topic_embeddings= {}
#     for topic_id,sentences in grouped.items():
#         combined_text = " ".join(sentences)
#         embedding = model.encode(combined_text, convert_to_tensor=True)
#         topic_embeddings[topic_id]= embedding
#     return topic_embeddings
        
# embeddings1= get_topic_embeddings(grouped1)
# embeddings2= get_topic_embeddings(grouped2)

# #using cosine similarity to match topic pairs

# similarity_threshold = 0.7
# matches = []

# for id1,emb1 in embeddings1.items():
#     for id2,emb2 in embeddings2.items():
#         score = util.cos_sim(emb1, emb2).item()
#         if score > similarity_threshold:
#             matches.append((id1, id2, score))
            
# #printing matches:
# matches.sort(key=lambda x: -x[2])  # Sort by similarity score in descending order of similarity
# for m in matches:
#     print(f"Match : File1 Topic {m[0]} <----> File2 Topic{m[1]} with similarity : {m[2]:.4f}")
   
# #collecting matched topic ids                
# matched_ids_1 = set(m[0] for m in matches)
# matched_ids_2 = set(m[1] for m in matches)

# #create new merged topic dictionary
# merged_topics = defaultdict(lambda: {"label": "", "paragraphs": []})
# topic_counter = 0

# #adding merged topics  
# for id1, id2, score in matches:
#     topic_id = f"merged_topic_{topic_counter}"
    
#     merged_para= grouped1[id1]+["++++"]+ grouped2[id2]  
#     # ++++ seperates paragraphs from different files
#     label1 = topic_labels1.get(id1, f"Topic {id1}")
#     label2 = topic_labels2.get(id2, f"Topic {id2}")
#     merged_label = f"{label1} /  {label2}"      
#     # / separates labels from different files
    
#     merged_topics[topic_id]["label"]= merged_label
#     merged_topics[topic_id]["paragraphs"] = merged_para
    
#     topic_counter += 1
    
# #adding non-matched    
# for id1 , paras in grouped1.items():
#     if id1 not in matched_ids_1:
#         topic_id = f"file1_topic_{topic_counter}"
#         merged_topics[topic_id]["label"]= topic_labels1.get(id1,f"Topic {id1}")
#         merged_topics[topic_id]["paragraphs"] = paras
#         topic_counter += 1
        
        
# for id2 , paras in grouped2.items():
#     if id2 not in matched_ids_2:
#         topic_id = f"file2_topic_{topic_counter}"
#         merged_topics[topic_id]["label"]= topic_labels2.get(id2,f"Topic {id2}")
#         merged_topics[topic_id]["paragraphs"] = paras
#         topic_counter += 1
        
        

    
# def export_pdf_json(merged_topics, output_folder="generated",base_filename ="merged_output"):
#     try:
#         #create folder if not existing
#         os.makedirs(output_folder, exist_ok=True)
        
#         pdf_path = os.path.join(output_folder, f"{base_filename}")
#         json_path = os.path.join(output_folder, f"{base_filename}.json")
        
#         #create json file
#         with open(json_path, "w", encoding="utf-8") as f:
#             json.dump(merged_topics, f, ensure_ascii=False, indent=4)
        
#         #create pdf file
#         pdf = FPDF()
#         pdf.set_auto_page_break(auto=True, margin=15)
#         pdf.set_left_margin(10)
#         pdf.set_right_margin(10)
#         pdf.set_auto_page_break(auto=True, margin=15)
#         pdf.add_page()
#         pdf.add_page()
#         pdf.add_font('TiemposTextRegular', '', 'fonts/TiemposTextRegular.ttf', uni=True)
#         pdf.set_font("TiemposTextRegular", size=12)

#         for topic_id, content in merged_topics.items():
#             label = content.get("label", f"Topic {topic_id}")
#             paragraphs = content.get("paragraphs", [])

#             pdf.set_font("TiemposTextRegular", size=14)
#             pdf.multi_cell(0, 10, f"{topic_id}: {label}\n")

#             pdf.set_font("TiemposTextRegular", size=12)
#             for para in paragraphs:
#                 pdf.multi_cell(0, 8, f"- {para}")
#             pdf.ln(5)

#         pdf.output(f"{pdf_path}.pdf")
#         print(f"✅ Exported: \nPDF: {pdf_path}\nJSON: {json_path}")
#     finally:
#         pdf.close()
    
    
# export_pdf_json(merged_topics, output_folder="generated", base_filename="merged_output")

from textwrap import wrap
from clustering import group_sentences
import os
import json
from fpdf import FPDF
import fitz

from sentence_transformers import SentenceTransformer,util
from collections import defaultdict

#initialize model
model = SentenceTransformer('all-mpnet-base-v2')

grouped1, topic_labels1 = group_sentences("docu.pdf",contains_header= True,contains_footer=True,output_prefix="output1")
grouped2, topic_labels2 = group_sentences("docu2.pdf",contains_header = True,contains_footer = False,output_prefix="output2")

def get_topic_embeddings(grouped):
    topic_embeddings= {}
    for topic_id,sentences in grouped.items():
        combined_text = " ".join(sentences)
        embedding = model.encode(combined_text, convert_to_tensor=True)
        topic_embeddings[topic_id]= embedding
    return topic_embeddings
        
embeddings1= get_topic_embeddings(grouped1)
embeddings2= get_topic_embeddings(grouped2)

#using cosine similarity to match topic pairs

similarity_threshold = 0.7
matches = []

for id1,emb1 in embeddings1.items():
    for id2,emb2 in embeddings2.items():
        score = util.cos_sim(emb1, emb2).item()
        if score > similarity_threshold:
            matches.append((id1, id2, score))
            
#printing matches:
matches.sort(key=lambda x: -x[2])  # Sort by similarity score in descending order of similarity
for m in matches:
    print(f"Match : File1 Topic {m[0]} <----> File2 Topic{m[1]} with similarity : {m[2]:.4f}")
   
#collecting matched topic ids                
matched_ids_1 = set(m[0] for m in matches)
matched_ids_2 = set(m[1] for m in matches)

#create new merged topic dictionary
merged_topics = defaultdict(lambda: {"label": "", "paragraphs": []})
topic_counter = 0

#adding merged topics  
for id1, id2, score in matches:
    topic_id = f"merged_topic_{topic_counter}"
    
    merged_para= grouped1[id1]+["++++"]+ grouped2[id2]  
    # ++++ seperates paragraphs from different files
    label1 = topic_labels1.get(id1, f"Topic {id1}")
    label2 = topic_labels2.get(id2, f"Topic {id2}")
    merged_label = f"{label1} /  {label2}"      
    # / separates labels from different files
    
    merged_topics[topic_id]["label"]= merged_label
    merged_topics[topic_id]["paragraphs"] = merged_para
    
    topic_counter += 1
    
#adding non-matched    
for id1 , paras in grouped1.items():
    if id1 not in matched_ids_1:
        topic_id = f"file1_topic_{topic_counter}"
        merged_topics[topic_id]["label"]= topic_labels1.get(id1,f"Topic {id1}")
        merged_topics[topic_id]["paragraphs"] = paras
        topic_counter += 1
        
        
for id2 , paras in grouped2.items():
    if id2 not in matched_ids_2:
        topic_id = f"file2_topic_{topic_counter}"
        merged_topics[topic_id]["label"]= topic_labels2.get(id2,f"Topic {id2}")
        merged_topics[topic_id]["paragraphs"] = paras
        topic_counter += 1
        
        

    
def export_pdf_json(merged_topics, output_folder="generated",base_filename ="merged_output"):
    
        #create folder if not existing
        os.makedirs(output_folder, exist_ok=True)
        
        pdf_path = os.path.join(output_folder, f"{base_filename}")
        json_path = os.path.join(output_folder, f"{base_filename}.json")
        
        #create json file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(merged_topics, f, ensure_ascii=False, indent=4)
        
        try:
            #create pdf file
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=5)
            pdf.add_page()
            pdf.add_font('TiemposTextRegular', '', 'fonts/TiemposTextRegular.ttf')
            pdf.set_font("TiemposTextRegular", size=12)

            for topic_id, content in merged_topics.items():
                label = content.get("label", f"Topic {topic_id}")
                paragraphs = content.get("paragraphs", [])

                pdf.set_font("TiemposTextRegular", size=14)
                pdf.multi_cell(0, 10, f"{topic_id}: {label}\n")

                pdf.set_font("TiemposTextRegular", size=12)
                for para in paragraphs:
                    try:
                        if isinstance(para, str) and para.strip():
                            # Skip if it's a long word with no spaces
                            if len(para) > 100 and ' ' not in para:
                                print(f"⚠️ Skipping unbreakable line: {para[:30]}...")
                                continue
                            # Use multi_cell directly; it wraps text automatically
                            pdf.multi_cell(0, 8, f"- {para}", new_x="LEFT", new_y="NEXT")
                    except Exception as e:
                        print(f"⚠️ Skipped a paragraph due to FPDF error: {e}")
                pdf.ln(5)

            pdf.output(f"{pdf_path}.pdf")
            print(f"✅ Exported: \nPDF: {pdf_path}\nJSON: {json_path}")
        finally:
            print("Closing PDF file...")
            
    
export_pdf_json(merged_topics, output_folder="generated", base_filename="merged_output")