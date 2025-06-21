from training import train_model

# input_texts = [
#     "This is the first input text.",
#     "Here is another example of input text.",
#     "The third input text is also here."
# ]

# target_texts = [
#     "This is the first target text.",
#     "Here is another example of target text.",
#     "The third target text is also here."
# ]


#train the model
# model, input_tokenizer, output_tokenizer, history = train_model(
#     input_texts=input_texts,
#     target_texts=target_texts,
#     num_words=10000,
#     max_input_len=300,
#     max_output_len=400,
#     embedding_dim=256,
#     lstm_units=512,
#     epochs=50,
#     batch_size=32,
#     validation_split=0.2,
# )

# Save the trained model and tokenizers
# model.save("bilstm_attention_model.h5")

# import pickle
# with open("input_tokenizer.pkl", "wb") as f:
#     pickle.dump(input_tokenizer, f)
# with open("output_tokenizer.pkl", "wb") as f:
#     pickle.dump(output_tokenizer, f)


data1= """Engineering is a profession that applies mathematics and science to utilize the properties of
matter and sources of energy to create useful structures, machines, products, systems and
processes (Davis and Cornwell, 2010).
Engineering may be defined as the application, under constraints of scientific principles, to
the planning, design, construction, and operation of structures, equipment, and systems for
the benefit of society ( Sincero and Sincero, 1996).
Engineering is the profession in which a knowledge of the mathematical and natural
sciences gained by study, experience, and practice is applied with judgment to develop ways
to economically utilize the materials and forces of nature for the benefit of human society.
In other words, Engineering may be defined as the application, under constraints of
scientific principles, to the planning, design, construction and operation of structures,
equipment and systems for the benefit of the society.
If the tasks performed by environmental engineers were examined, it would be found that
the engineers deal with the structures, equipment and systems that are designed to protect
and enhance the quality of the environment and to protect and enhance public health and
welfare.
"""
data2 ="""Engineering is a profession that applies mathematics and science to utilize the properties of matter
and sources of energy to create useful structures, machines, products, systems and processes
(Davis and Cornwell, 2010).
Engineering may be defined as the application, under constraints of scientific principles to the
planning, design, construction, and operation of structures, equipment, and systems for the benefit
of society ( Sincero and Sincero, 1996).
Engineering is the profession in which a knowledge of the mathematical and natural sciences
gained by study, experience, and practice is applied with judgment to develop ways to utilize
economically the materials and forces of nature for the benefit of human society.
In other words, Engineering may be defined as the application, under constraints of scientific
principles to the planning, design, construction and operation of structures, equipment and
systems for the benefit of the society. If the tasks performed by environmental engineers were
examined, it would be found that the engineers deal with the structures, equipment and systems
that are designed to protect and enhance the quality of the environment and to protect and enhance
public health and welfare."""

mrgd = """Engineering is a profession that applies mathematics and science to utilize the properties of matter and sources of energy to create useful structures, machines, products, systems, and processes (Davis and Cornwell, 2010). It is defined as the application, under constraints of scientific principles, to the planning, design, construction, and operation of structures, equipment, and systems for the benefit of society (Sincero and Sincero, 1996). This profession involves applying knowledge of mathematical and natural sciences—gained through study, experience, and practice—with sound judgment to economically utilize materials and the forces of nature for human welfare. In other words, engineering seeks to apply scientific principles under practical constraints to design and operate systems that serve society's needs. Specifically, environmental engineers work with structures, equipment, and systems aimed at protecting and enhancing environmental quality, public health, and general welfare."""

from training import train_model

model , input_tokenizer, output_tokenizer, history = train_model(
    input_texts = [data1, data2],
    target_texts = mrgd,
    epochs= 30
)