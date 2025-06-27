import json
from fpdf import FPDF

# Load your cleaned JSON data
with open("cleaned_merged_topics.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Create a PDF class
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Cleaned Merged Topics Dataset", ln=True, align="C")
        self.ln(5)

    def add_entry(self, key, label, input_text, output_text):
        self.set_font("Arial", "B", 11)
        self.multi_cell(0, 8, f"Key: {key}", border=0)
        self.multi_cell(0, 8, f"Label: {label}", border=0)

        self.set_font("Arial", "", 10)
        self.multi_cell(0, 8, f"Input:\n{input_text}", border=1)
        self.ln(2)
        self.multi_cell(0, 8, f"Output:\n{output_text}", border=1)
        self.ln(10)

# Initialize PDF
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Loop through entries
for entry in data:
    pdf.add_entry(
        key=entry.get("key", ""),
        label=entry.get("label", ""),
        input_text=entry.get("input", ""),
        output_text=entry.get("output", "")
    )

# Save the file
pdf.output("cleaned_merged_output.pdf")
print("✅ PDF created: cleaned_merged_output.pdf")
