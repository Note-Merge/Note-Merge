# import json
# import re

# def split_topics_by_word_limit(
#     input_path="merged_output.json",
#     output_path="merged_split.json",
#     max_words_per_chunk=350
# ):
#     """
#     Reads a JSON file, splits 'merged_topic_' entries into smaller chunks based on a
#     word count, and appends the untouched 'file_topic_' entries to the end of the file.

#     This function dynamically adds full paragraphs to each chunk until the word limit
#     is reached, ensuring chunks are balanced and have a consistent length.
    
#     It now also preserves any topics containing '_topic_' (but not 'merged_') without modification.

#     Args:
#         input_path (str): The path to the input JSON file.
#         output_path (str): The path where the processed JSON file will be saved.
#         max_words_per_chunk (int): The target maximum word count for each new chunk.
#     """
#     print(f"Starting data processing with word limit...")
#     print(f"Input file: {input_path}")
#     print(f"Output file: {output_path}")
#     print(f"Max words per chunk: {max_words_per_chunk}")

#     try:
#         with open(input_path, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         print(f"Error: The input file was not found at '{input_path}'")
#         return
#     except json.JSONDecodeError:
#         print(f"Error: The file at '{input_path}' is not a valid JSON file.")
#         return

#     processed_data = {}
#     file_topics_data = {} # A separate dictionary to hold file_topics and preserve order

#     # Helper to count words
#     def count_words(text):
#         return len(text.split())

#     for topic_id, content in data.items():
#         # *** FIX: Check more flexibly for file topics (e.g., 'file1_topic_', 'file2_topic_') ***
#         if "_topic_" in topic_id and "merged_" not in topic_id:
#             print(f"\nFound file topic, copying untouched: {topic_id}...")
#             file_topics_data[topic_id] = content
#             continue

#         # This part of the code will now only run for 'merged_topic_' entries
#         print(f"\nProcessing merged topic: {topic_id}...")
#         original_paragraphs = content.get('paragraphs', [])
        
#         try:
#             separator_index = original_paragraphs.index("++++")
#         except ValueError:
#             print(f"  - Warning: Skipping topic '{topic_id}' because it has no '++++' separator.")
#             continue
            
#         units_before = [p.strip() for p in original_paragraphs[:separator_index] if p.strip()]
#         units_after = [p.strip() for p in original_paragraphs[separator_index + 1:] if p.strip()]
        
#         if not units_before or not units_after:
#             print(f"  - Warning: Skipping topic '{topic_id}' because it lacks content on both sides of '++++'.")
#             continue

#         print(f"  - Found {len(units_before)} paragraph units before '++++' and {len(units_after)} after.")
        
#         chunk_counter = 0
#         while units_before or units_after:
#             current_chunk_before = []
#             current_chunk_after = []
#             current_word_count = 0
            
#             temp_units_before = list(units_before)
#             temp_units_after = list(units_after)

#             while True:
#                 can_add_before = False
#                 can_add_after = False

#                 if temp_units_before:
#                     next_unit_len = count_words(temp_units_before[0])
#                     if current_word_count + next_unit_len <= max_words_per_chunk:
#                         can_add_before = True
                
#                 if temp_units_after:
#                     next_unit_len = count_words(temp_units_after[0])
#                     if current_word_count + next_unit_len <= max_words_per_chunk:
#                         can_add_after = True

#                 if can_add_before and (not can_add_after or len(temp_units_before) >= len(temp_units_after)):
#                     unit = temp_units_before.pop(0)
#                     current_chunk_before.append(unit)
#                     current_word_count += count_words(unit)
#                 elif can_add_after:
#                     unit = temp_units_after.pop(0)
#                     current_chunk_after.append(unit)
#                     current_word_count += count_words(unit)
#                 else:
#                     break
            
#             if current_chunk_before and current_chunk_after:
#                 new_paragraphs_list = current_chunk_before + ["++++"] + current_chunk_after
#                 new_key = f"{topic_id}_{chunk_counter}"
                
#                 processed_data[new_key] = {
#                     "label": content.get("label", "N/A"),
#                     "paragraphs": new_paragraphs_list
#                 }
#                 chunk_counter += 1
#                 units_before = list(temp_units_before)
#                 units_after = list(temp_units_after)
#             else:
#                 if units_before:
#                     long_unit = units_before.pop(0)
#                     print(f"  - Discarding a 'before' paragraph of {count_words(long_unit)} words to prevent stall.")
#                 elif units_after:
#                     long_unit = units_after.pop(0)
#                     print(f"  - Discarding an 'after' paragraph of {count_words(long_unit)} words to prevent stall.")
#                 else:
#                     break

#         print(f"  - Created {chunk_counter} new balanced chunks with a word limit of ~{max_words_per_chunk}.")

#     # Add the untouched 'file_topic_' entries to the very end of the processed data
#     if file_topics_data:
#         print("\nAdding all 'file_topic_' entries to the end of the file...")
#         processed_data.update(file_topics_data)

#     try:
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(processed_data, f, indent=4)
#         print(f"\nSuccessfully processed all topics and saved the output to '{output_path}'")
#     except IOError as e:
#         print(f"\nError: Could not write to the file at '{output_path}'. Reason: {e}")

# # --- Example of how to run the script ---
# if __name__ == "__main__":
#     split_topics_by_word_limit(
#         input_path="merged_output.json",
#         output_path="merged_split.json",
#         max_words_per_chunk=350
#     )


import json
import re

def split_all_topics_by_word_limit(
    input_path="merged_output.json",
    output_path="merged_split.json",
    max_words_per_chunk=350
):
    """
    Reads a JSON file and splits ALL topics ('merged_topic_' and 'file_topic_')
    into smaller chunks based on a maximum word count, preserving the original structure.

    - 'merged_topic_' entries are split into balanced chunks around the '++++' separator.
    - 'file_topic_' entries are split sequentially if they exceed the word limit.

    Args:
        input_path (str): The path to the input JSON file.
        output_path (str): The path where the processed JSON file will be saved.
        max_words_per_chunk (int): The target maximum word count for each new chunk.
    """
    print(f"Starting data processing with word limit for ALL topics...")
    print(f"Input file: {input_path}")
    print(f"Output file: {output_path}")
    print(f"Max words per chunk: {max_words_per_chunk}")

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The input file was not found at '{input_path}'")
        return
    except json.JSONDecodeError:
        print(f"Error: The file at '{input_path}' is not a valid JSON file.")
        return

    processed_data = {}

    def count_words(text):
        return len(text.split())

    for topic_id, content in data.items():
        original_paragraphs = content.get('paragraphs', [])
        total_words = sum(count_words(p) for p in original_paragraphs if p != "++++")

        # --- Logic for 'merged_topic_' entries ---
        if topic_id.startswith("merged_"):
            print(f"\nProcessing merged topic: {topic_id}...")
            
            try:
                separator_index = original_paragraphs.index("++++")
            except ValueError:
                print(f"  - Warning: Skipping merged topic '{topic_id}' because it has no '++++' separator.")
                continue
                
            units_before = [p.strip() for p in original_paragraphs[:separator_index] if p.strip()]
            units_after = [p.strip() for p in original_paragraphs[separator_index + 1:] if p.strip()]
            
            if not units_before or not units_after:
                print(f"  - Warning: Skipping merged topic '{topic_id}' because it lacks content on both sides of '++++'.")
                continue

            print(f"  - Found {len(units_before)} paragraphs before '++++' and {len(units_after)} after.")
            
            chunk_counter = 0
            while units_before or units_after:
                current_chunk_before, current_chunk_after, current_word_count = [], [], 0
                temp_units_before, temp_units_after = list(units_before), list(units_after)

                while True:
                    can_add_before = temp_units_before and current_word_count + count_words(temp_units_before[0]) <= max_words_per_chunk
                    can_add_after = temp_units_after and current_word_count + count_words(temp_units_after[0]) <= max_words_per_chunk

                    if can_add_before and (not can_add_after or len(temp_units_before) >= len(temp_units_after)):
                        unit = temp_units_before.pop(0)
                        current_chunk_before.append(unit)
                        current_word_count += count_words(unit)
                    elif can_add_after:
                        unit = temp_units_after.pop(0)
                        current_chunk_after.append(unit)
                        current_word_count += count_words(unit)
                    else:
                        break
                
                if current_chunk_before and current_chunk_after:
                    processed_data[f"{topic_id}_{chunk_counter}"] = {
                        "label": content.get("label", "N/A"),
                        "paragraphs": current_chunk_before + ["++++"] + current_chunk_after
                    }
                    chunk_counter += 1
                    units_before, units_after = list(temp_units_before), list(temp_units_after)
                else:
                    if units_before: units_before.pop(0)
                    if units_after: units_after.pop(0)
                    if not units_before and not units_after: break
            
            print(f"  - Created {chunk_counter} new balanced chunks.")

        # --- Logic for 'file_topic_' entries ---
        else:
            print(f"\nProcessing file topic: {topic_id}...")
            if total_words <= max_words_per_chunk:
                print("  - Topic is within word limit, copying as is.")
                processed_data[topic_id] = content
            else:
                print(f"  - Topic exceeds word limit ({total_words} words), splitting...")
                chunk_counter = 0
                units = [p.strip() for p in original_paragraphs if p.strip()]
                
                while units:
                    current_chunk_paragraphs, current_word_count = [], 0
                    while units:
                        next_unit_len = count_words(units[0])
                        if current_word_count + next_unit_len <= max_words_per_chunk or not current_chunk_paragraphs:
                            unit = units.pop(0)
                            current_chunk_paragraphs.append(unit)
                            current_word_count += count_words(unit)
                        else:
                            break
                    
                    if current_chunk_paragraphs:
                        processed_data[f"{topic_id}_{chunk_counter}"] = {
                            "label": content.get("label", "N/A"),
                            "paragraphs": current_chunk_paragraphs
                        }
                        chunk_counter += 1
                print(f"  - Created {chunk_counter} new chunks.")

    # Save the processed data
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=4)
        print(f"\nSuccessfully processed all topics and saved the output to '{output_path}'")
    except IOError as e:
        print(f"\nError: Could not write to the file at '{output_path}'. Reason: {e}")

# --- Example of how to run the script ---
if __name__ == "__main__":
    split_all_topics_by_word_limit(
        input_path="merged_output.json",
        output_path="merged_split.json",
        max_words_per_chunk=350
    )
