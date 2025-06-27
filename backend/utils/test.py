import clustering

grouped1, topic_labels1 = clustering.group_sentences("docu2.pdf", contains_header=True, contains_footer=True, output_prefix="test1")
print(grouped1)